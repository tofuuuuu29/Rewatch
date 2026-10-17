from rest_framework.test import APITestCase

from config.testutils import client_for, make_user
from movies.models import Movie


class MovieOwnershipTests(APITestCase):

    def setUp(self):
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.alice_client = client_for(self.alice)
        self.bob_client = client_for(self.bob)

    def test_new_title_belongs_to_me_and_defaults_to_watching(self):
        response = self.alice_client.post('/api/movies/', {'movie_name': 'Inception'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'watching')
        self.assertEqual(Movie.objects.get(pk=response.data['id']).user, self.alice)

    def test_user_cannot_set_the_owner_themselves(self):
        response = self.alice_client.post('/api/movies/', {
            'movie_name': 'Inception', 'user': self.bob.id
        }, format='json')

        self.assertEqual(Movie.objects.get(pk=response.data['id']).user, self.alice)

    def test_list_only_shows_my_own_titles(self):
        Movie.objects.create(movie_name='Alice movie', user=self.alice)
        Movie.objects.create(movie_name='Bob movie', user=self.bob)

        response = self.alice_client.get('/api/movies/')

        self.assertEqual([m['movie_name'] for m in response.data], ['Alice movie'])

    def test_other_users_title_is_hidden(self):
        movie = Movie.objects.create(movie_name='Alice movie', user=self.alice)
        url = f'/api/movies/{movie.id}/'

        self.assertEqual(self.bob_client.get(url).status_code, 404)
        self.assertEqual(
            self.bob_client.put(url, {'movie_name': 'Hijacked'}, format='json').status_code, 404
        )
        self.assertEqual(self.bob_client.delete(url).status_code, 404)
        self.assertTrue(Movie.objects.filter(pk=movie.id, movie_name='Alice movie').exists())

    def test_mark_completed_and_delete_my_own_title(self):
        movie = Movie.objects.create(movie_name='Inception', user=self.alice)
        url = f'/api/movies/{movie.id}/'

        response = self.alice_client.put(url, {'movie_name': 'Inception', 'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'completed')

        self.assertEqual(self.alice_client.delete(url).status_code, 204)
        self.assertFalse(Movie.objects.filter(pk=movie.id).exists())

    def test_invalid_status_is_rejected(self):
        response = self.alice_client.post('/api/movies/', {
            'movie_name': 'Inception', 'status': 'bogus'
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.data)


class MovieValidationTests(APITestCase):
    """These need config/serializers.py and the context={'request': request} change."""

    def setUp(self):
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.alice_client = client_for(self.alice)

    def test_duplicate_title_is_rejected(self):
        Movie.objects.create(movie_name='Inception', user=self.alice)

        response = self.alice_client.post('/api/movies/', {'movie_name': 'Inception'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('movie_name', response.data)

    def test_duplicate_title_ignores_letter_case(self):
        Movie.objects.create(movie_name='Inception', user=self.alice)

        response = self.alice_client.post('/api/movies/', {'movie_name': 'INCEPTION'}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_another_user_can_use_the_same_title(self):
        Movie.objects.create(movie_name='Inception', user=self.bob)

        response = self.alice_client.post('/api/movies/', {'movie_name': 'Inception'}, format='json')

        self.assertEqual(response.status_code, 201)

    def test_blank_title_is_rejected(self):
        for name in ('', '   '):
            with self.subTest(name=name):
                response = self.alice_client.post('/api/movies/', {'movie_name': name}, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('movie_name', response.data)

    def test_saving_a_title_with_its_own_name_is_fine(self):
        movie = Movie.objects.create(movie_name='Inception', user=self.alice)

        response = self.alice_client.put(
            f'/api/movies/{movie.id}/', {'movie_name': 'Inception', 'status': 'completed'}, format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_renaming_to_another_of_my_titles_is_rejected(self):
        Movie.objects.create(movie_name='Inception', user=self.alice)
        other = Movie.objects.create(movie_name='Matrix', user=self.alice)

        response = self.alice_client.put(
            f'/api/movies/{other.id}/', {'movie_name': 'inception'}, format='json'
        )

        self.assertEqual(response.status_code, 400)