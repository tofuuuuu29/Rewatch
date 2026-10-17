from rest_framework.test import APITestCase

from config.testutils import client_for, make_user
from kdrama.models import Kdrama


class SeasonEpisodeTests(APITestCase):
    """K-Drama, anime and TV series share the same season / episode rules."""

    # url -> name of the title field
    ENDPOINTS = {
        '/api/kdrama/': 'kdrama_name',
        '/api/anime/': 'anime_name',
        '/api/tvseries/': 'tv_series',
    }

    def setUp(self):
        self.user = make_user('alice')
        self.api = client_for(self.user)

    def test_season_and_episode_can_be_left_blank(self):
        for url, name_field in self.ENDPOINTS.items():
            with self.subTest(url=url):
                # left out completely
                response = self.api.post(url, {name_field: 'No season'}, format='json')
                self.assertEqual(response.status_code, 201)
                self.assertIsNone(response.data['season'])
                self.assertIsNone(response.data['episode'])

                # sent as null (what the frontend sends for an empty box)
                response = self.api.post(
                    url, {name_field: 'Null season', 'season': None, 'episode': None}, format='json'
                )
                self.assertEqual(response.status_code, 201)

    def test_season_and_episode_are_saved(self):
        for url, name_field in self.ENDPOINTS.items():
            with self.subTest(url=url):
                response = self.api.post(
                    url, {name_field: 'With season', 'season': 2, 'episode': 5}, format='json'
                )
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.data['season'], 2)
                self.assertEqual(response.data['episode'], 5)

    def test_season_and_episode_must_be_at_least_1(self):
        for url, name_field in self.ENDPOINTS.items():
            for field in ('season', 'episode'):
                for bad in (0, -1):
                    with self.subTest(url=url, field=field, value=bad):
                        response = self.api.post(
                            url, {name_field: 'Bad number', field: bad}, format='json'
                        )
                        self.assertEqual(response.status_code, 400)
                        self.assertIn(field, response.data)

    def test_kdrama_progress_can_be_updated(self):
        drama = Kdrama.objects.create(kdrama_name='Crash Landing on You', user=self.user)

        response = self.api.put(f'/api/kdrama/{drama.id}/', {
            'kdrama_name': 'Crash Landing on You', 'season': 1, 'episode': 4
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['episode'], 4)