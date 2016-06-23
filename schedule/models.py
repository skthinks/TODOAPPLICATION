
from django.db import models


class Users(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=25)
    verified = models.BooleanField(default=False)


class Schedule(models.Model):
    user = models.ForeignKey('Users', related_name='u_id')
    task = models.CharField(max_length=100)
    scheduled_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    checked = models.BooleanField(default=True)

    class Meta:
        ordering = ('scheduled_time',)
