import datetime
from decimal import Decimal
import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator

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
    item_quantity = models.PositiveIntegerField(default=1) #check later to see if this is needed at all
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
        for compartment in self.CompartmentsDetails.all():
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
        for content in self.FridgeContent.all():
            item_vol = content.item_length * content.item_width * content.item_height * content.quantity
            occupied += item_vol
        return occupied
    
    @property
    def usage_percent(self):
        """
        Calculates the percentage of the fridge's total volume that is currently occupied.
        """
        total_volume = self.total_volume
        occupied_volume = self.occupied_volume
        return (occupied_volume / total_volume * 100) if total_volume > 0 else 0
    
    def total_items_volume(self):
        """
        Calculates the total volume of all items inside the fridge.
        """
        total_items_volume = Decimal("0")
        for content in self.FridgeContent.all():
            item_vol = content.item_length * content.item_width * content.item_height * content.quantity
            total_items_volume += item_vol
        return total_items_volume
    
    


class FridgeDetail(models.Model):
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="FridgeDetails")
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
    

class CompartmentsDetails(models.Model):
    compartment_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="CompartmentsDetails")
    compartment_name = models.CharField(max_length=200)
    compartment_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    compartment_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    compartment_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    
    @property
    def occupied(self):
        occupied = Decimal("0")
        # Accessing related fridge contents via the related_name "fridge_contents"
        for content in self.FridgeContent.all():
            item_vol = content.item_length * content.item_width * content.item_height * content.quantity
            occupied += item_vol
        print(f"Occupied volume in {self.compartment_name}: {occupied}")
        return occupied
    
    @property
    def usage_ratio(self):
        try:
            return (self.occupied / self.total_vol) * 100
        except (ZeroDivisionError):
            return Decimal("0")
    
    @property
    def total_vol(self):
        return self.compartment_height * self.compartment_length * self.compartment_width
        
    def total_items_volume(self):
        """
        Calculates the total volume of all items inside this compartment.
        """
        total_items_volume = Decimal("0")
        for content in self.FridgeContent.all():
            item_vol = content.item_length * content.item_width * content.item_height * content.quantity
            total_items_volume += item_vol
        return total_items_volume
    
    def __str__(self): 
        return f"{self.compartment_name}"


class FamilyTag(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, related_name="FamilyTag")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="FamilyTag")
    limit_ratio = models.DecimalField(max_digits=3, decimal_places=2, default=0.30)
    
    class Meta:
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        unique_together = ("family", "user")

    def calculate_user_percent(self):
        """
        Calculate the percentage of the fridge's total volume occupied by this user's items.
        """
        user_items = FridgeContent.objects.filter(user=self.user, family_id=self.family)
        user_volume = sum(
            item.item_length * item.item_width * item.item_height * item.quantity
            for item in user_items
        )
        total_volume = self.family.total_volume
        return (user_volume / total_volume * 100) if total_volume > 0 else 0

    def calculate_user_limit_space(self):
        """
        Calculate the user's allowed space in the fridge based on their limit ratio.
        """
        if self.family.owner == self.user:
            # No limit for the family owner
            return self.family.total_volume
        return self.family.total_volume * self.limit_ratio
    
    @staticmethod
    def get_all_families_by_user(user):
        return Family.objects.filter(FamilyTag__user=user)
        
    def __str__(self):
        return f"{self.family} : {self.user} "



# Fridge Content Model
class FridgeContent(models.Model):
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="FridgeContent")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="FridgeContent")
    compartment_id = models.ForeignKey(CompartmentsDetails, on_delete=models.CASCADE, related_name="FridgeContent")
    item_id = models.ForeignKey(ItemsDetails, on_delete=models.CASCADE, related_name="FridgeContent")
    quantity = models.PositiveIntegerField(default=1)
    item_description = models.TextField(null=True, blank=True)
    item_length = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    item_width = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    item_height = models.DecimalField(default=1, max_digits=5, decimal_places=2)
    expiration_date = models.DateField(null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    location = models.CharField(max_length=50, default='fridge')  #not fully implemented yet
    
    def will_expire_soon(self):
        if self.expiration_date:
            return self.expiration_date <= timezone.now().date() + datetime.timedelta(days=4)
        return False

    
    
    @property
    def volume(self):
        """Calculate the volume of a single item."""
        if self.item_length is None or self.item_width is None or self.item_height is None:
            return 0  # Default to 0 if any dimension is missing
        return self.item_length * self.item_width * self.item_height
    
    @classmethod
    def items_added_by(cls, member, family):
        return cls.objects.filter(user=member, family_id=family)
    
    @classmethod
    def items_added_in(cls,compartment, family):
        return cls.objects.filter(compartment_id=compartment, family_id=family)

    class Meta:
        unique_together = (
            'family_id', 
            'compartment_id', 
            'item_id', 
            'expiration_date', 
            'quantity', 
            'item_description'
            )
        verbose_name = "Fridge Content"
        verbose_name_plural = "Fridge Contents"

    def __str__(self):
        return f"{self.item_id} ({self.quantity}) in {self.family_id.family_name}"


# class UserProfile(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="UserProfile")
#     profile_picture = models.ImageField(upload_to='', blank=True)

#     def __str__(self):
#         return f"{self.user} has {self.profile_picture} for their profile picture and is limited to {self.overall_space} overall."



class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True,   
        blank=True,
    )
    profile_picture = models.ImageField(
        blank=True,
        upload_to='', 
    )

    def __str__(self):
        return f"{self.user} has {self.profile_picture} for their profile picture and is limited to {self.overall_space} overall."

# # Automatically create or save profile when user is created or updated
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#     else:
#         instance.profile.save()

