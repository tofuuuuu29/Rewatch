"""Searches TMDB (movies, TV series, K-dramas) and AniList (anime) for titles,
and lists what is trending for the login page slideshow.

The TMDB key is read from the TMDB_API_KEY environment variable, or from a file
called tmdb_key.txt next to manage.py. It never goes to the browser.
AniList needs no key.
"""
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from django.conf import settings
from django.core.cache import cache

TMDB_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE = 'https://image.tmdb.org/t/p/w342'
ANILIST_URL = 'https://graphql.anilist.co'
TIMEOUT = 5
CACHE_SECONDS = 600
LIMIT = 8

CATEGORIES = ('movies', 'anime', 'kdrama', 'tvseries')

ANILIST_QUERY = """
query ($search: String, $perPage: Int) {
  Page(page: 1, perPage: $perPage) {
    media(search: $search, type: ANIME, sort: SEARCH_MATCH, isAdult: false) {
      title { romaji english }
      startDate { year }
      coverImage { large }
      description(asHtml: false)
    }
  }
}
"""


class DiscoverError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.message = message
        self.status = status


def tmdb_key():
    key = os.environ.get('TMDB_API_KEY', '').strip()
    if key:
        return key

    path = Path(settings.BASE_DIR) / 'tmdb_key.txt'
    if path.exists():
        raw = path.read_bytes()
        # Notepad / PowerShell may save with a BOM or as UTF-16; handle all of them
        if raw.startswith((b'\xff\xfe', b'\xfe\xff')) or b'\x00' in raw:
            text = raw.decode('utf-16', errors='ignore')
        else:
            text = raw.decode('utf-8-sig', errors='ignore')
        # first line only, without spaces or quotes
        return (text.strip().splitlines() or [''])[0].strip().strip('"\'')

    return ''


def get_json(url, headers=None, body=None, service='The search service'):
    """GET a URL, or POST JSON when `body` is given. Gives up after TIMEOUT seconds."""
    all_headers = {'Accept': 'application/json', 'User-Agent': 'Rewatch/1.0 (class project)', **(headers or {})}
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        all_headers['Content-Type'] = 'application/json'

    request = urllib.request.Request(url, data=data, headers=all_headers)

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 401 and service == 'TMDB':
            raise DiscoverError('TMDB rejected the API key. Check the key in tmdb_key.txt.', 502)
        if e.code == 429:
            raise DiscoverError('Too many searches. Wait a moment and try again.', 429)
        raise DiscoverError(f'{service} returned an error ({e.code}).', 502)
    except (urllib.error.URLError, TimeoutError, OSError):
        raise DiscoverError(f'{service} is slow or unreachable right now. Try again in a moment.', 502)
    except ValueError:
        raise DiscoverError(f'{service} sent an unreadable answer.', 502)


def search_tmdb(category, query):
    key = tmdb_key()
    if not key:
        raise DiscoverError(
            'No TMDB key yet. Put your TMDB API key in a file called tmdb_key.txt next to manage.py.',
            503,
        )

    kind = 'movie' if category == 'movies' else 'tv'
    params = {'query': query, 'include_adult': 'false', 'language': 'en-US', 'page': 1}
    headers = {}

    # a v3 key goes in the URL; the long "read access token" goes in a header
    if key.startswith('eyJ'):
        headers['Authorization'] = f'Bearer {key}'
    else:
        params['api_key'] = key

    data = get_json(f'{TMDB_URL}/search/{kind}?{urllib.parse.urlencode(params)}', headers, service='TMDB')

    results = []
    for item in data.get('results', []):
        if category == 'kdrama' and item.get('original_language') != 'ko':
            continue

        title = item.get('title') or item.get('name')
        if not title:
            continue

        date = item.get('release_date') or item.get('first_air_date') or ''
        poster = item.get('poster_path')
        results.append({
            'title': title,
            'year': date[:4],
            'poster_url': f'{TMDB_IMAGE}{poster}' if poster else '',
            'overview': (item.get('overview') or '')[:240],
            'source': 'TMDB',
        })

    return results[:LIMIT]


def search_anilist(query):
    body = {'query': ANILIST_QUERY, 'variables': {'search': query, 'perPage': LIMIT}}
    data = get_json(ANILIST_URL, body=body, service='AniList')

    media = (((data or {}).get('data') or {}).get('Page') or {}).get('media') or []

    results = []
    for item in media:
        names = item.get('title') or {}
        title = names.get('english') or names.get('romaji')
        if not title:
            continue

        year = (item.get('startDate') or {}).get('year') or ''
        cover = (item.get('coverImage') or {}).get('large') or ''
        # AniList descriptions can contain <br> and other tags
        overview = re.sub(r'<[^>]+>', ' ', item.get('description') or '')
        overview = re.sub(r'\s+', ' ', overview).strip()

        results.append({
            'title': title,
            'year': str(year),
            'poster_url': cover,
            'overview': overview[:240],
            'source': 'AniList',
        })

    return results[:LIMIT]


def search(category, query):
    cache_key = 'discover:' + hashlib.md5(f'{category}|{query.lower()}'.encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    results = search_anilist(query) if category == 'anime' else search_tmdb(category, query)
    cache.set(cache_key, results, CACHE_SECONDS)
    return results


# ---------------------------------------------------------------------------
# Trending (login page slideshow). Public, so it is cached for a few hours.
# ---------------------------------------------------------------------------
TMDB_BACKDROP = 'https://image.tmdb.org/t/p/w1280'
TRENDING_CACHE_SECONDS = 3 * 60 * 60
TRENDING_PER_CATEGORY = 3

ANILIST_TRENDING_QUERY = """
query ($perPage: Int) {
  Page(page: 1, perPage: $perPage) {
    media(type: ANIME, sort: TRENDING_DESC, isAdult: false) {
      title { romaji english }
      startDate { year }
      bannerImage
      coverImage { extraLarge large }
    }
  }
}
"""


def tmdb_get(path, extra_params):
    key = tmdb_key()
    if not key:
        raise DiscoverError('No TMDB key.', 503)

    params = {'language': 'en-US', 'page': 1, **extra_params}
    headers = {}
    if key.startswith('eyJ'):
        headers['Authorization'] = f'Bearer {key}'
    else:
        params['api_key'] = key

    return get_json(f'{TMDB_URL}{path}?{urllib.parse.urlencode(params)}', headers, service='TMDB')


def tmdb_slides(path, extra_params, label):
    data = tmdb_get(path, extra_params)

    slides = []
    for item in data.get('results', []):
        title = item.get('title') or item.get('name')
        backdrop = item.get('backdrop_path')
        if not title or not backdrop:
            continue

        date = item.get('release_date') or item.get('first_air_date') or ''
        slides.append({
            'title': title,
            'year': date[:4],
            'category': label,
            'image_url': f'{TMDB_BACKDROP}{backdrop}',
            'source': 'TMDB',
        })

    return slides[:TRENDING_PER_CATEGORY]


def anilist_slides():
    body = {'query': ANILIST_TRENDING_QUERY, 'variables': {'perPage': 12}}
    data = get_json(ANILIST_URL, body=body, service='AniList')
    media = (((data or {}).get('data') or {}).get('Page') or {}).get('media') or []

    slides = []
    for item in media:
        names = item.get('title') or {}
        title = names.get('english') or names.get('romaji')
        cover = item.get('coverImage') or {}
        image = cover.get('extraLarge') or cover.get('large') or item.get('bannerImage')
        if not title or not image:
            continue

        slides.append({
            'title': title,
            'year': str((item.get('startDate') or {}).get('year') or ''),
            'category': 'Anime',
            'image_url': image,
            'source': 'AniList',
        })

    return slides[:TRENDING_PER_CATEGORY]


def safe(fetch):
    """One source failing must not hide the others."""
    try:
        return fetch()
    except DiscoverError:
        return []


def trending():
    cached = cache.get('discover:trending')
    if cached is not None:
        return cached

    fetchers = [
        lambda: tmdb_slides('/trending/movie/week', {}, 'Movie'),
        anilist_slides,
        lambda: tmdb_slides('/discover/tv', {'with_original_language': 'ko', 'sort_by': 'popularity.desc'}, 'K-Drama'),
    ]

    # run the three requests at the same time so the page never waits for all of them in turn
    with ThreadPoolExecutor(max_workers=len(fetchers)) as pool:
        groups = list(pool.map(lambda f: safe(f), fetchers))

    # mix them: movie, anime, k-drama, movie, anime, k-drama ...
    slides = []
    for i in range(TRENDING_PER_CATEGORY):
        for group in groups:
            if i < len(group):
                slides.append(group[i])

    if slides:  # never cache an empty answer
        cache.set('discover:trending', slides, TRENDING_CACHE_SECONDS)
    return slides