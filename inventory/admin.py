from django.contrib import admin

from .models import ItemsDetails, Family, FamilyTag, FridgeContent, FridgeDetail, UserProfile

# Register your models here.
admin.site.register(ItemsDetails)
admin.site.register(Family)
admin.site.register(FamilyTag)
admin.site.register(FridgeContent)
admin.site.register(FridgeDetail)
admin.site.register(UserProfile)