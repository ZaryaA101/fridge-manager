from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import CreateUserForm, ProfileForm

from .decorators import unauthenticated_user

from .models import ItemsDetails
from . import models
from django.contrib.auth.models import User 

# Create your views here.
@unauthenticated_user
def loginPage(request):    
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user=user)
            return redirect('fridgePage')
        else:
            messages.info(request, "Username or password is incorrect.")
            return render(request, 'loginPage.html') 
        
    return render(request, 'loginPage.html')


def logoutUser(request):
    logout(request)
    return redirect('LoginPage')


@unauthenticated_user
def heroPage(request):    
    form = CreateUserForm()
    
    if request.method == "POST":    
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            return redirect('LoginPage')
        
    context = {'form': form}
    
    return render(request, 'heroPage.html', context = context)

@login_required(login_url='heroPage')
def fridgePage(request):
    item_list = ItemsDetails.objects.order_by("item_type")

    context = {
        "item_list": item_list,
    }
    return render(request, "fridgePage.html", context)
  
@login_required(login_url='heroPage')
def home(request):
    families = models.Family.objects.filter(familytag__user=request.user)
    family_users = models.FamilyTag.objects.filter(family_id__in=families)
    context = {
        "family_users": family_users,
        "families": families,
        
    }
    return render(request, "home.html", context=context)

@login_required(login_url='heroPage')
def addFridge(request):
    fridge_list=1
    context = {
        "fridge_list": fridge_list,
    }
    return render(request, "addFridge.html", context=context)

@login_required(login_url='heroPage')
def profilePage(request):

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm()

    context = {
        'User': User,
        'form': form
    }

    return render(request, 'profilePage.html', context)
