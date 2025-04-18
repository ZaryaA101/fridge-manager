from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import UserProfile

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

 