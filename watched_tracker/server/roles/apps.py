from django.apps import AppConfig
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
