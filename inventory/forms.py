from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import UserProfile, FridgeContent, ItemsDetails, CompartmentsDetails

import django.forms as forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']
    
class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
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
        
    def __init__(self, *args, **kwargs):
        # pop off the family (or user/request) you pass in
        family = kwargs.pop('family', None)
        super().__init__(*args, **kwargs)
        if family is not None:
            # only show compartments for this family
            self.fields['compartment_id'].queryset = CompartmentsDetails.objects.filter(family_id=family)
