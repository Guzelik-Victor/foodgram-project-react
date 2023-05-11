from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class CustomUser(AbstractUser):
    email = models.EmailField('email address', max_length=254)
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followings',
    )

    class Meta:
        UniqueConstraint(fields=['user', 'author'], name='unique_follow')

    def __str__(self):
        return f'{self.user} - {self.author}'



