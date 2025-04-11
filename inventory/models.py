import datetime

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User 
import uuid


# Create your models here.
class ItemsDetails(models.Model):
    item_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    item_name = models.CharField(max_length=200)
    #item_image =
    item_description = models.TextField(null=True, blank=True) 
    created = models.DateTimeField(auto_now_add=True)
    dimension_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    dimension_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    dimension_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    
    
    class Meta:
        verbose_name = "Item Detail"
        verbose_name_plural = "Item Details"

    def will_expire_soon(self):
        return self.exp_date >= timezone.now() - datetime.timedelta(days=4)
    
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


class FridgeDetail(models.Model):
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="FridgeDetails")
    compartment_name = models.CharField(max_length=200)
    compartment_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    compartment_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    compartment_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    added_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.family_id.family_name}'s Fridge details"
    

# Fridge Content Model
class FridgeContent(models.Model):
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="fridge_contents")
    
    item_id = models.ForeignKey(ItemsDetails, on_delete=models.CASCADE, related_name="item_details")
    quantity = models.PositiveIntegerField(default=1)
    item_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    item_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    item_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    expiration_date = models.DateField(null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        verbose_name = "Fridge Content"
        verbose_name_plural = "Fridge Contents"

    def __str__(self):
        return f"{self.item_id} ({self.quantity}) in {self.family_id.family_name}"