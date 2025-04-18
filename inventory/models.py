import datetime
from decimal import Decimal
import uuid

from django.db import models
from django.utils import timezone


from django.contrib.auth.models import User 


# Create your models here.
class ItemsDetails(models.Model):
    Item_Type_Choices = [
        ('Produce', 'Produce'),
        ('Freezer', 'Freezer'),
        ('Left Shelves', 'Left Shelves'),
        ('Middle Shelves', 'Middle Shelves'),
        ('Right Shelves', 'Right Shelves'),
    ]
    item_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    item_name = models.CharField(max_length=200)
    item_image = models.ImageField(upload_to='', default='default.jpeg')
    item_description = models.TextField(null=True, blank=True) 
    item_expiration = models.DateField(null=True, blank=True)
    item_type = models.CharField(max_length=30, choices = Item_Type_Choices, default='Produce')
    created = models.DateTimeField(auto_now_add=True)
    dimension_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    dimension_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    dimension_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    
    class Meta:
        verbose_name = "Item Detail"
        verbose_name_plural = "Item Details"
    
    def __str__(self):
        return self.item_name    


class Family(models.Model):
    family_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    family_name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"

    def __str__(self):
        return f"{self.family_name}"
    
    @property
    def total_volume(self):
        """
        Calculates the total available volume from all compartments in this family's fridge.
        """
        total = Decimal("0")
        # Accessing related compartments via the related_name "FridgeDetails"
        for compartment in self.FridgeDetails.all():
            comp_vol = compartment.compartment_length * compartment.compartment_width * compartment.compartment_height
            total += comp_vol
        return total

    @property
    def occupied_volume(self):
        """
        Calculates the total volume occupied by items in the family's fridge.
        """
        occupied = Decimal("0")
        # Accessing related fridge contents via the related_name "fridge_contents"
        for content in self.fridge_contents.all():
            item_vol = content.item_length * content.item_width * content.item_height * content.quantity
            occupied += item_vol
        return occupied


class FridgeDetail(models.Model):
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="FridgeDetails")
    compartment_name = models.CharField(max_length=200)
    compartment_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    compartment_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    compartment_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    added_date = models.DateTimeField(auto_now_add=True)
    capacity = models.PositiveIntegerField(default=100)  # WHATTTT ex capacity
    current_item_count = models.PositiveIntegerField(default=0)
    
    def is_full(self):
        return self.current_item_count >= self.capacity

    def update_item_count(self, count):
        new_count = self.current_item_count + count
        if new_count < 0:
            new_count = 0  
        self.current_item_count = new_count
        self.save()


    def __str__(self):
        return f"{self.family_id.family_name}'s Fridge details"
    


class FamilyTag(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    limit_ratio = models.DecimalField(max_digits=3, decimal_places=2, default=0.30)
    
    class Meta:
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        unique_together = ("family", "user")
        
    @staticmethod
    def get_all_families_by_user(user):
        return Family.objects.filter(familytag__user=user)
        
    
    def __str__(self):
        return f"{self.family} : {self.user} "



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
    
    def will_expire_soon(self):
        if self.expiration_date:
            return self.expiration_date <= timezone.now().date() + datetime.timedelta(days=4)
        return False

    class Meta:
        verbose_name = "Fridge Content"
        verbose_name_plural = "Fridge Contents"

    def __str__(self):
        return f"{self.item_id} ({self.quantity}) in {self.family_id.family_name}"


class UserProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="user_profile")
    overall_space = models.DecimalField(default=1, max_digits=2, decimal_places=2)
    leftdoor_space = models.DecimalField(default=1, max_digits=2, decimal_places=2)
    rightdoor_space = models.DecimalField(default=1, max_digits=2, decimal_places=2)
    producebin_space = models.DecimalField(default=1, max_digits=2, decimal_places=2)
    freezer_space = models.DecimalField(default=1, max_digits=2, decimal_places=2)
