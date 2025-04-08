import datetime

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User 
import uuid


# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=30)
    exp_date = models.DateField("Expiration date")
    description = models.CharField(max_length=200)

    def will_expire_soon(self):
        return self.exp_date >= timezone.now() - datetime.timedelta(days=4)

    def __str__(self):
        return self.name


class ItemsDetails(models.Model):
    item_name = models.CharField(max_length=200)
    #item_image =
    item_description = models.TextField(null=True, blank=True) 
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    class Meta:
        verbose_name = "Item Detail"
        verbose_name_plural = "Item Details"

    def __str__(self):
        return self.item_name    
    

class Family(models.Model):
    family_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    family_name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"

    def __str__(self):
        return f"{self.family_name}"
    
    
class FamilyTag(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        unique_together = ("family", "user")
    
    def __str__(self):
        return f"{self.family} : {self.user} "
    

# Fridge Content Model
class FridgeContent(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="fridge_contents")
    item_id = models.ForeignKey(ItemsDetails, on_delete=models.CASCADE, related_name="item_details")
    quantity = models.PositiveIntegerField(default=1)
    expiration_date = models.DateField(null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fridge Content"
        verbose_name_plural = "Fridge Contents"

    def __str__(self):
        return f"{self.item_id} ({self.quantity}) in {self.family.family_name}"