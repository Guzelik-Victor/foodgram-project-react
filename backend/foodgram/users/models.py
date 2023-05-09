from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class CustomUser(AbstractUser):
    email = models.EmailField('email address', max_length=254)
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
    )




