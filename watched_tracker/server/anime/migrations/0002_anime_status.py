from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='anime',
            name='status',
            field=models.CharField(
                choices=[('watching', 'Watching'), ('completed', 'Completed')],
                default='watching',
                max_length=20,
            ),
        ),
    ]
