from rest_framework.test import APITestCase

from config.testutils import client_for, make_user
from roles.models import Roles
from users.models import User


class AuthTests(APITestCase):

    def test_register_gives_the_user_role(self):
        response = self.client.post('/api/users/', {
            'username': 'newbie', 'password': 'pass12345'
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        self.assertEqual(User.objects.get(username='newbie').role.name, 'User')

    def test_register_cannot_choose_admin_role(self):
        admin_role, _ = Roles.objects.get_or_create(name='Admin')

        self.client.post('/api/users/', {
            'username': 'sneaky', 'password': 'pass12345', 'role': admin_role.id
        }, format='json')

        self.assertEqual(User.objects.get(username='sneaky').role.name, 'User')

    def test_register_without_password_fails(self):
        response = self.client.post('/api/users/', {'username': 'nopass'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_login_returns_tokens(self):
        make_user('sam', password='pass12345')

        response = self.client.post('/api/login/', {
            'username': 'sam', 'password': 'pass12345'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password_fails(self):
        make_user('sam', password='pass12345')

        response = self.client.post('/api/login/', {
            'username': 'sam', 'password': 'wrong'
        }, format='json')

        self.assertEqual(response.status_code, 401)

    def test_request_without_token_is_rejected(self):
        self.assertEqual(self.client.get('/api/users/').status_code, 401)
        self.assertEqual(self.client.get('/api/movies/').status_code, 401)


class UserPermissionTests(APITestCase):
    """These need the admin-only change in users/views.py."""

    def setUp(self):
        self.admin = make_user('boss', admin=True)
        self.normal = make_user('sam')

    def test_normal_user_cannot_list_users(self):
        response = client_for(self.normal).get('/api/users/')
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_view_a_user(self):
        response = client_for(self.normal).get(f'/api/users/{self.admin.id}/')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_users(self):
        response = client_for(self.admin).get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_admin_can_edit_a_user_without_a_password(self):
        response = client_for(self.admin).put(
            f'/api/users/{self.normal.id}/', {'username': 'sam2'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(pk=self.normal.id).username, 'sam2')

    def test_normal_user_cannot_create_a_role(self):
        response = client_for(self.normal).post('/api/roles/', {'name': 'Hacker'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_superuser_automatically_gets_the_admin_role(self):
        superuser = User.objects.create_superuser(username='root', password='pass12345')
        self.assertEqual(superuser.role.name, 'Admin')