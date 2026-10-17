from rest_framework.test import APIClient

from roles.models import Roles
from users.models import User


def make_user(username, admin=False, password='pass12345'):
    """Create a user with the Admin or User role."""
    role, _ = Roles.objects.get_or_create(name='Admin' if admin else 'User')
    return User.objects.create_user(username=username, password=password, role=role)


def client_for(user):
    """An API client that is already logged in as `user`."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client