from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, ProfileForm, FridgeContentForm

from decimal import Decimal
from .decorators import unauthenticated_user

from .models import ItemsDetails, FridgeDetail, FridgeContent
from . import models
from django.contrib.auth.models import User 

import datetime
from datetime import date

# Create your views here.
@unauthenticated_user
def loginPage(request):    
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user=user)
            return redirect('home')
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

            #Create userprofile instance
            models.UserProfile.objects.create(
                user=get_object_or_404(User, username=username)
            )

            return redirect('LoginPage')
        
    context = {'form': form}
    
    return render(request, 'heroPage.html', context = context)


@login_required(login_url='heroPage')  # send anonymous users to your real login form
def fridgePage(request, family_id):
    family = get_object_or_404(models.Family, pk=family_id)
    profile, _ = models.UserProfile.objects.get_or_create(user=request.user)

    #Fetch compartments and FridgeDetail
    compartments = models.CompartmentsDetails.objects.filter(family_id=family)
    fridge = FridgeDetail.objects.filter(family_id=family).first()  # returns None if missing

    #Compute expirations and usage
    today = date.today()
    expiring_items = FridgeContent.objects.filter(
        family_id=family,
        expiration_date__lte=today + datetime.timedelta(days=4)
    )
    usage_percent = (family.occupied_volume / family.total_volume * 100) if fridge else 0

    #All fridge contents
    item_list = FridgeContent.objects.filter(family_id=family)

    #Get user limit ratio
    tag = models.FamilyTag.objects.get(user=request.user, family=family)
    if tag.limit_ratio and request.user != family.owner:
        limit_fraction = tag.limit_ratio
    else:
        limit_fraction = 1

    # Get all user's fridge items
    user_items = FridgeContent.objects.filter(user=request.user)

    #Calculate user usage percent
    user_volume = 0
    for item in user_items:
        user_volume += item.item_length * item.item_width * item.item_height * item.quantity

    user_percent = (user_volume / family.total_volume * 100) if fridge else 0

    return render(request, "fridgePage.html", {
        "family":         family,
        "profile":        profile,
        "compartments":   compartments,
        "fridge":         fridge,
        "expiring_items": expiring_items,
        "usage_percent":  usage_percent,
        "today":          today,
        "item_list":      item_list,
        "limit_fraction": limit_fraction*100,
        "user_limit_space": limit_fraction*family.total_volume, 
        "user_percent":   user_percent,
    })
  
@login_required(login_url='heroPage')
def home(request):
    families = models.Family.objects.filter(FamilyTag__user=request.user)
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

    profile = get_object_or_404(models.UserProfile, user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'User': User,
        'form': form,
        'profile': profile,
    }

    return render(request, 'profilePage.html', context)


@login_required(login_url='heroPage')
def createFamily(request):
    if request.method == 'POST':
        family_name = request.POST.get('family_name', '').strip()
 
        # Owner default to logged in user
        owner_id = request.POST.get('owner')
        if owner_id:
            owner = get_object_or_404(User, pk=owner_id)
        else:
            owner = request.user

        if not family_name:
            context = {
                'error': 'Family name is required.',
                'users': User.objects.all()
            }
            return render(request, 'createFamily.html', context)
        
         # Check if a Family with this name already exists.
        if models.Family.objects.filter(family_name__iexact=family_name).exists():
            context = {
                'error': 'A family with that name already exists.',
                'users': User.objects.all()
            }
            return render(request, 'createFamily.html', context)

        # Create the new Family instance
        new_family = models.Family.objects.create(
            family_name=family_name,
            owner=owner
        )
        
        # Add the current user as a family member using FamilyTag.
        models.FamilyTag.objects.create(
            family=new_family,
            user=request.user
        )

        # Create new FridgeDetail instance
        models.FridgeDetail.objects.create(
            family_id=new_family
        )

        #Create the 5 default compartments
        models.CompartmentsDetails.objects.create(
            family_id=new_family,
            compartment_name="Left Shelves",
            compartment_length=12,
            compartment_width=5,
            compartment_height=6
            )
        
        models.CompartmentsDetails.objects.create(
            family_id=new_family,
            compartment_name="Middle Shelves",
            compartment_length=15,
            compartment_width=15,
            compartment_height=12
            )
        
        models.CompartmentsDetails.objects.create(
            family_id=new_family,
            compartment_name="Right Shelves",
            compartment_length=12,
            compartment_width=5,
            compartment_height=6
            )
        
        models.CompartmentsDetails.objects.create(
            family_id=new_family,
            compartment_name="Produce",
            compartment_length=15,
            compartment_width=15,
            compartment_height=12
            )
        
        models.CompartmentsDetails.objects.create(
            family_id=new_family,
            compartment_name="Freezer",
            compartment_length=15,
            compartment_width=15,
            compartment_height=12
            )

        return redirect('home')
    
    context = {}
    return render(request, 'createFamily.html', context)



@login_required(login_url='heroPage')
def manageFamilyMembers(request, family_id):
    family = get_object_or_404(models.Family, family_id=family_id)
    
    # Only allow the family owner to manage members.
    if family.owner != request.user:
        return HttpResponseForbidden("You do not have permission to manage this family.")
    
    if request.method == "POST":
        # Adding a member
        if "add_member" in request.POST:
            member_id = request.POST.get("member_id")
            limit_ratio = request.POST.get("limit_ratio", "0.30")  
            if member_id:
                if not models.FamilyTag.objects.filter(family=family, user__id=member_id).exists():
                    member = get_object_or_404(User, id=member_id)
                    models.FamilyTag.objects.create(family=family, user=member, limit_ratio=limit_ratio)
                    
        # Removing a member
        elif "remove_member" in request.POST:
            remove_id = request.POST.get("remove_member")
            if remove_id:
                # Prevent removing the owner.
                if str(family.owner.id) == remove_id:
                    pass
                else:
                    models.FamilyTag.objects.filter(family=family, user__id=remove_id).delete()
        # Updating a member's limit ratio
        elif "update_ratio" in request.POST:
            member_id = request.POST.get("member_id")
            new_ratio = request.POST.get("new_ratio")
            if member_id and new_ratio:
                tag = models.FamilyTag.objects.filter(family=family, user__id=member_id).first()
                if tag:
                    tag.limit_ratio = new_ratio
                    tag.save()
                    
        elif 'transfer_owner' in request.POST:
            new_owner_id = request.POST['transfer_owner']
            new_owner = User.objects.get(pk=new_owner_id)
            family.owner = new_owner
            family.save()
            messages.success(request, f"Ownership transferred to {new_owner.username}.")
            #return redirect('manageFamilyMembers', family_id=family.family_id)
            return redirect('home')
                            
        # Redirect to the same page after handling POST
        return redirect("manageFamilyMembers", family_id=family.family_id)
    
    #GET REQUEST
    current_members = list(models.FamilyTag.objects.filter(family=family).select_related('user'))
    owner_id = family.owner.id
    #make owner to always in front
    current_members.sort(key=lambda tag: 0 if tag.user.id == owner_id else 1)
    current_member_ids = [tag.user.id for tag in current_members if tag.user]
    
    available_users = User.objects.exclude(id__in=current_member_ids)
    default_limit_ratio = 0.30 
    
    context = {
        "family": family,
        "current_members": current_members,
        "available_users": available_users,
        "default_limit_ratio": default_limit_ratio,
    }
    return render(request, "manageFamilyMembers.html", context)



@login_required(login_url='heroPage')
def my_families(request):
    # Retrieve all Family instances where the current user is a member using the static method.
    families = models.FamilyTag.get_all_families_by_user(request.user)
    
    context = {
        'families': families
    }
    return render(request, 'my_families.html', context)


@login_required(login_url='heroPage')
def manage_fridge_details(request, family_id):
    family = get_object_or_404(models.Family, family_id=family_id)
    
    # Only allow the owner to manage fridge details.
    if family.owner != request.user:
        return HttpResponseForbidden("You do not have permission to manage this family's fridge details.")
    
    error = None

    if request.method == 'POST':
        # Handle adding a new compartment.
        if "add_compartment" in request.POST:
            compartment_name = request.POST.get('compartment_name', '').strip()
            compartment_length = request.POST.get('compartment_length')
            compartment_width = request.POST.get('compartment_width')
            compartment_height = request.POST.get('compartment_height')
            
            # Validate that the compartment name is provided.
            if not compartment_name:
                error = "Compartment name is required."
            else:
                # Create the new CompartmentDetails record
                models.CompartmentsDetails.objects.create(
                    family_id=family,
                    compartment_name=compartment_name,
                    compartment_length=compartment_length,
                    compartment_width=compartment_width,
                    compartment_height=compartment_height
                )
        
        # remove compartment
        elif "remove_compartment" in request.POST:
            detail_id = request.POST.get("remove_compartment")
            print(f"details_id: {detail_id}")
            if detail_id:
                models.CompartmentsDetails.objects.filter(pk=detail_id).delete()
        
        # Redirect to the same management page (to avoid resubmission issues)
        return redirect('manage_fridge_details', family_id=family.family_id)
    
    # For GET requests, fetch the current fridge details.
    fridge_details = models.CompartmentsDetails.objects.filter(family_id=family)
    
    context = {
        "family": family,
        "fridge_details": fridge_details,
        "error": error
    }
    return render(request, "manage_fridge_details.html", context)



