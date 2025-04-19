from django import forms
from inventory.models import ItemsDetails

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemsDetails
        fields = [
            'item_name', 
            'item_image', 
            'item_description', 
            'item_expiration',
            'item_type', 
            'dimension_length', 
            'dimension_width', 
            'dimension_height'
        ]
