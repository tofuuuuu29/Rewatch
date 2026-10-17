from rest_framework.test import APITestCase

from config.testutils import client_for, make_user
from movies.models import Movie
from type.models import Type


class TypeTests(APITestCase):

    def setUp(self):
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.alice_client = client_for(self.alice)
        self.alice_movie = Movie.objects.create(movie_name='Alice movie', user=self.alice)
        self.bob_movie = Movie.objects.create(movie_name='Bob movie', user=self.bob)

    def test_can_link_my_own_title(self):
        response = self.alice_client.post('/api/type/', {'movie': self.alice_movie.id}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_cannot_link_someone_elses_title(self):
        response = self.alice_client.post('/api/type/', {'movie': self.bob_movie.id}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_exactly_one_title_must_be_chosen(self):
        self.assertEqual(self.alice_client.post('/api/type/', {}, format='json').status_code, 400)

    def test_list_only_shows_my_own_types(self):
        Type.objects.create(movie=self.alice_movie)
        Type.objects.create(movie=self.bob_movie)

        response = self.alice_client.get('/api/type/')

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], self.alice_movie.id)