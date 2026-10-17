"""Adds the watch-list feature to your Django server.

Run it ONCE from the server folder (the one with manage.py):
    python apply_watched.py
It is safe to run twice. It only touches:
  config/settings.py, config/urls.py, config/permissions.py, roles/apps.py,
  and the views.py of movies / anime / kdrama / tvseries.
"""
import pathlib
import re
import sys

if not pathlib.Path('manage.py').exists() or not pathlib.Path('watched/models.py').exists():
    sys.exit('Run this from the server folder, with the "watched" folder next to manage.py.')

problems = []

# 1. settings: register the app
p = pathlib.Path('config/settings.py')
s = p.read_text(encoding='utf-8')
if "'watched'" in s:
    print('settings.py: already done')
else:
    new, n = re.subn(r"(INSTALLED_APPS\s*=\s*\[.*?)(\n\])", r"\1\n    'watched',\2", s, count=1, flags=re.S)
    if n:
        p.write_text(new, encoding='utf-8')
        print('settings.py: added watched')
    else:
        problems.append("settings.py: add  'watched',  to the end of INSTALLED_APPS")

# 2. urls: add the route
p = pathlib.Path('config/urls.py')
s = p.read_text(encoding='utf-8')
if 'watched.urls' in s:
    print('urls.py: already done')
else:
    new, n = re.subn(r"(\n(\s*)path\('api/type/', include\('type\.urls'\)\),)",
                     r"\1\n\n\2# Watched (each user's own watch list)\n\2path('api/watched/', include('watched.urls')),",
                     s, count=1)
    if n:
        p.write_text(new, encoding='utf-8')
        print('urls.py: added api/watched/')
    else:
        problems.append("urls.py: add  path('api/watched/', include('watched.urls')),  inside urlpatterns")

# 3. permissions helper used by the watched views
pathlib.Path('config/permissions.py').write_text('''from rest_framework.permissions import BasePermission


def user_is_admin(user):
    return bool(
        user
        and user.is_authenticated
        and user.role is not None
        and user.role.name.lower() == 'admin'
    )


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return user_is_admin(request.user)
''', encoding='utf-8')
print('permissions.py: written')

# 4. roles: Admin/User roles exist, superusers become Admin
pathlib.Path('roles/apps.py').write_text('''from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_roles(sender, **kwargs):
    """Make sure the Admin and User roles exist (registration needs 'User')."""
    from roles.models import Roles
    from users.models import User

    for name in ('Admin', 'User'):
        if not Roles.objects.filter(name__iexact=name).exists():
            Roles.objects.create(name=name)

    # superusers made before the roles existed have no role: make them Admin
    admin_role = Roles.objects.get(name__iexact='Admin')
    User.objects.filter(is_superuser=True, role__isnull=True).update(role=admin_role)


class RolesConfig(AppConfig):
    name = 'roles'

    def ready(self):
        post_migrate.connect(create_default_roles, sender=self)
''', encoding='utf-8')
print('roles/apps.py: written')

# 5. any logged-in user can ADD a title; only admins edit / delete
old = re.compile(r"if self\.request\.method == 'GET':(\s+)return \[IsAuthenticated\(\)\]")
for app in ('movies', 'anime', 'kdrama', 'tvseries'):
    p = pathlib.Path(app, 'views.py')
    s = p.read_text(encoding='utf-8')
    if "method in ('GET', 'POST')" in s:
        print(f'{app}/views.py: already done')
        continue
    new, n = old.subn(r"if self.request.method in ('GET', 'POST'):\1return [IsAuthenticated()]", s, count=1)
    if n:
        p.write_text(new, encoding='utf-8')
        print(f'{app}/views.py: logged-in users can add titles')
    else:
        problems.append(f"{app}/views.py: in the list view's get_permissions change  == 'GET'  to  in ('GET', 'POST')")

print()
if problems:
    print('DONE, but please do these by hand:')
    for x in problems:
        print('  -', x)
else:
    print('All done. Now run:  python manage.py migrate')
