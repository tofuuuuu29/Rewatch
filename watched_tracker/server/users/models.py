from django.contrib.auth.models import AbstractUser
from django.db import models
from roles.models import Roles


class User(AbstractUser):
    gender = models.CharField(max_length=20, blank=True)

    role = models.ForeignKey(
        Roles,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        # a superuser made with `createsuperuser` has no role, so the API
        # would treat it as a normal user. Give it the Admin role.
        if self.is_superuser and self.role is None:
            self.role = Roles.objects.filter(name__iexact='Admin').first()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'users'
