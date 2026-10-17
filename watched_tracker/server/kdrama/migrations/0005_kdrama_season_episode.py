from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kdrama', '0004_kdrama_assign_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='kdrama',
            name='season',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='kdrama',
            name='episode',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]