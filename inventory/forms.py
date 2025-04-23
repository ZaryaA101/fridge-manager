from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import UserProfile, FridgeContent, ItemsDetails

import django.forms as forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']
    
class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'overall_space',
            'leftdoor_space',
            'rightdoor_space',
            'producebin_space',
            'freezer_space'
        ]

class FridgeContentForm(ModelForm):
    item_id = forms.ModelChoiceField(
        queryset=ItemsDetails.objects.all(),
        label="Select Item",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = FridgeContent
        fields = ['item_id', 'compartment_id', 'quantity', 'expiration_date']
        widgets = {
            'compartment_id': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }