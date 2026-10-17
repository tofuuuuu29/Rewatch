import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('type', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('watching', 'Watching'), ('completed', 'Completed'), ('plan_to_watch', 'Plan to watch'), ('dropped', 'Dropped')], default='plan_to_watch', max_length=20)),
                ('rating', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('season', models.PositiveIntegerField(blank=True, null=True)),
                ('episode', models.PositiveIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('date_started', models.DateField(blank=True, null=True)),
                ('date_finished', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(db_column='type_id', on_delete=django.db.models.deletion.CASCADE, to='type.type')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='watched', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'watched',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='watchentry',
            constraint=models.UniqueConstraint(fields=('user', 'type'), name='unique_user_type'),
        ),
    ]
