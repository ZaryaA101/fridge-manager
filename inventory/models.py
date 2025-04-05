import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=30)
    exp_date = models.DateField("Expiration date")
    description = models.CharField(max_length=200)

    def will_expire_soon(self):
        return self.exp_date >= timezone.now() - datetime.timedelta(days=4)

    def __str__(self):
        return self.name