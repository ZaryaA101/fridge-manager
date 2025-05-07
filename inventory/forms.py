from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import UserProfile, FridgeContent, ItemsDetails, CompartmentsDetails
from django.core.exceptions import ValidationError

import django.forms as forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']
    
class ProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        label="Profile picture",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep your current password."
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password')
        p2 = cleaned.get('confirm_password')
        if (p1 or p2) and p1 != p2:
            raise ValidationError("New passwords do not match.")
        return cleaned

    def save(self, commit=True):
        # 1) Save the User object
        user = super().save(commit=False)
        new_pw = self.cleaned_data.get('new_password')
        if new_pw:
            user.set_password(new_pw)
        if commit:
            user.save()

        # 2) Now save the picture onto the UserProfile
        profile_pic = self.cleaned_data.get('profile_picture')
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile_pic:
            profile.profile_picture = profile_pic
            profile.save()

        return user
    

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
