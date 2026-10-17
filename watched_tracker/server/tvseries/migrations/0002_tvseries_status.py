from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tvseries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tvseries',
            name='status',
            field=models.CharField(
                choices=[('watching', 'Watching'), ('completed', 'Completed')],
                default='watching',
                max_length=20,
            ),
        ),
    ]
