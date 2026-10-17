# Watched Tracker

```
watched_tracker/
├── docs/     this file + Hoppscotch collection and environment
├── server/   Django REST API (users, roles, anime, movies, kdrama, tvseries, type)
└── web/      Vue 3 + TypeScript + Tailwind frontend
```

## 1. Run the API (server/)

```bash
cd server
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

Make sure PostgreSQL is running with the database from `config/settings.py` (`watched_tracker`), then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`migrate` creates the `Admin` and `User` roles by itself, and a superuser made with `createsuperuser` automatically gets the `Admin` role. Nothing to set up by hand.

## 2. Run the frontend (web/)

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5173` and log in with the superuser. The API address is `VITE_API_URL` in `web/.env`.

## 3. Test the API with Hoppscotch

1. In Hoppscotch open **Collections → Import → Import from Hoppscotch** and choose `docs/hoppscotch-collection.json`.
2. Open **Environments → Import** and choose `docs/hoppscotch-environment.json`, then select **Watched Tracker (local)** as the active environment.
3. Edit `adminUsername` and `adminPassword` in the environment to match the superuser you created. (`userUsername` / `userPassword` are for the normal test account, which the collection registers for you.)
4. Run the folders **in order, 1 to 10**. Requests save ids and tokens into the environment by themselves (`accessToken`, `movieId`, ...). Every request has a test that checks the status code.

| Folder | What it checks |
| --- | --- |
| 1 Auth | register, login (admin + normal user), wrong password, token refresh |
| 2 Users | list, get, update (no password needed), no-token request is rejected |
| 3 Roles | list, create, get, update |
| 4-7 Movies, Anime, K-Drama, TV Series | list, create, get, update, missing id returns 404 |
| 8 Type | create / get / update, two media at once is rejected |
| 9 Permissions | (outdated) still expects a normal user to get 403 on create / update / delete; that is no longer true, each user now manages their own titles |
| 10 Delete | deletes everything the earlier folders created |

## What was changed in the API

- Every title now belongs to the user who added it. Each user only sees and edits their own list (movies, anime, K-Drama, TV series and Type rows); there is no read-only role any more. Titles added before this change are given to the first superuser by migrations `0003_*_user.py` and `0004_*_assign_owner.py`.
- Every title (movie, anime, K-Drama, TV series) now has a `status`: `watching` (default) or `completed`. Run `python manage.py migrate` to add the column (`0002_*_status.py` in each app).

- Added `django-cors-headers` so the frontend can call the API (`config/settings.py`).
- `Admin` and `User` roles are created automatically after `migrate` (`roles/apps.py`).
- Superusers get the `Admin` role automatically (`users/models.py`).
- The password is now only required when registering, not when editing a user (`users/serializers.py`).

## Frontend overview (web/src)

- `config/site.ts` – the media types and their Django field names. Add a new type here.
- `axiosInstance.ts` – API client; attaches the token and refreshes it on a 401.
- `stores/auth.ts`, `stores/media.ts`, `stores/types.ts` – login / register, CRUD for every media type, and CRUD for the Type table.
- `router/index.ts` – routes and the login guard.
- `views/` – `auth/login`, `auth/register`, `dashboard`.

| Feature | API |
| --- | --- |
| Register | `POST /api/users/` |
| Login / refresh | `POST /api/login/`, `POST /api/token/refresh/` |
| Dashboard tabs, All / Watching / Completed filter | `GET /api/<type>/` |
| `+1 ep`, `Done` / `Resume` buttons | `PUT /api/<type>/<id>/` |
| Add / edit / delete (every user, own titles only) | `POST` / `PUT` / `DELETE` on `/api/<type>/` and `/api/<type>/<id>/` |
| Types tab (every user, own titles only) | `GET` / `POST /api/type/`, `PUT` / `DELETE /api/type/<id>/` |
| Users tab (admin only) | `GET /api/users/`, `GET /api/roles/`, `DELETE /api/users/<id>/` |
