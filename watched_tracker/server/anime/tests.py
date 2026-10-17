from rest_framework.test import APITestCase

from anime.models import Anime
from config.testutils import client_for, make_user


class AnimeTests(APITestCase):

    def setUp(self):
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.alice_client = client_for(self.alice)
        self.bob_client = client_for(self.bob)

    def test_create_with_season_and_episode(self):
        response = self.alice_client.post('/api/anime/', {
            'anime_name': 'Naruto', 'season': 1, 'episode': 3
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'watching')
        self.assertEqual(response.data['season'], 1)
        self.assertEqual(response.data['episode'], 3)
        self.assertEqual(Anime.objects.get(pk=response.data['id']).user, self.alice)

    def test_season_and_episode_can_be_blank(self):
        response = self.alice_client.post('/api/anime/', {
            'anime_name': 'Naruto', 'season': None, 'episode': None
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data['season'])
        self.assertIsNone(response.data['episode'])

    def test_season_and_episode_must_be_at_least_1(self):
        for field in ('season', 'episode'):
            with self.subTest(field=field):
                response = self.alice_client.post('/api/anime/', {
                    'anime_name': 'Naruto', field: 0
                }, format='json')

                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

    def test_plus_one_episode(self):
        anime = Anime.objects.create(anime_name='Naruto', season=1, episode=3, user=self.alice)

        response = self.alice_client.put(f'/api/anime/{anime.id}/', {
            'anime_name': 'Naruto', 'season': 1, 'episode': 4
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Anime.objects.get(pk=anime.id).episode, 4)

    def test_mark_completed(self):
        anime = Anime.objects.create(anime_name='Naruto', user=self.alice)

        response = self.alice_client.put(f'/api/anime/{anime.id}/', {
            'anime_name': 'Naruto', 'status': 'completed'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'completed')

    def test_list_only_shows_my_own_anime(self):
        Anime.objects.create(anime_name='Alice anime', user=self.alice)
        Anime.objects.create(anime_name='Bob anime', user=self.bob)

        response = self.alice_client.get('/api/anime/')

        self.assertEqual([a['anime_name'] for a in response.data], ['Alice anime'])

    def test_other_users_anime_is_hidden(self):
        anime = Anime.objects.create(anime_name='Alice anime', user=self.alice)
        url = f'/api/anime/{anime.id}/'

        self.assertEqual(self.bob_client.get(url).status_code, 404)
        self.assertEqual(
            self.bob_client.put(url, {'anime_name': 'Hijacked'}, format='json').status_code, 404
        )
        self.assertEqual(self.bob_client.delete(url).status_code, 404)

    def test_duplicate_title_is_rejected(self):
        """Needs the validation change (config/serializers.py)."""
        Anime.objects.create(anime_name='Naruto', user=self.alice)

        response = self.alice_client.post('/api/anime/', {'anime_name': 'NARUTO'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('anime_name', response.data)

    def test_another_user_can_use_the_same_title(self):
        Anime.objects.create(anime_name='Naruto', user=self.bob)

        response = self.alice_client.post('/api/anime/', {'anime_name': 'Naruto'}, format='json')

        self.assertEqual(response.status_code, 201)