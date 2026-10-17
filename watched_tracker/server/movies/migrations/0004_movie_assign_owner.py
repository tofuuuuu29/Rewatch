from django.conf import settings
from django.db import migrations


def give_existing_rows_an_owner(apps, schema_editor):
    # titles added before owners existed: give them to the first superuser
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Title = apps.get_model('movies', 'Movie')
    owner = User.objects.filter(is_superuser=True).order_by('id').first()
    if owner:
        Title.objects.filter(user__isnull=True).update(user=owner)


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_movie_user'),
    ]

    operations = [
        migrations.RunPython(give_existing_rows_an_owner, migrations.RunPython.noop),
    ]
