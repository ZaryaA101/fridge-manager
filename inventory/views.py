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
            return redirect('LoginPage')
        
    context = {'form': form}
    
    return render(request, 'heroPage.html', context = context)


@login_required(login_url='heroPage')
def fridgePage(request, family_id):
    #family = request.user.family_set.first()
    family = get_object_or_404(models.Family, family_id=family_id)
    compartments = models.CompartmentsDetails.objects.filter(family_id=family)
    
    try:
        fridge = FridgeDetail.objects.get(family_id=family)
    except FridgeDetail.DoesNotExist:
        fridge = None
    
    # Get today's date
    today = date.today()
    
    # Get items that will expire in the next 4 days
    expiring_items = FridgeContent.objects.filter(
        family_id=family,
        expiration_date__lte=today + datetime.timedelta(days=4)
    )
    # Calculate fridge capacity usage percentage
    if fridge:
        usage_percent = (fridge.current_item_count / fridge.capacity) * 100
    else:
        # Default to 0% if no fridge exists
        usage_percent = 0

    # Get all fridge items
    #fridge_items = FridgeContent.objects.filter(family_id=family)
        
    #item_list = ItemsDetails.objects.order_by("item_type")
    item_list = FridgeContent.objects.filter(family_id=family_id)
    return render(request, "fridgePage.html", {
        "expiring_items": expiring_items,  # List of expiring items
        #"fridge_items": fridge_items,  # List of all fridge items
        "usage_percent": usage_percent,  # Fridge capacity percentage
        "today": today,  # Today's date
        "item_list": item_list,
        "family": family,
        "compartments": compartments,
        
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

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm()

    context = {
        'User': User,
        'form': form,
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



def add_fridge_item(request, family_id):
    family = get_object_or_404(models.Family, pk=family_id)

    if request.method == "POST":
        form = FridgeContentForm(request.POST)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.family_id = family
            fridge_item.user      = request.user
            
            item: ItemsDetails = form.cleaned_data['item_id']
            fridge_item.item_length = item.dimension_length
            fridge_item.item_width = item.dimension_width
            fridge_item.item_height = item.dimension_height
            
            new_vol = (
                    fridge_item.item_length *
                    fridge_item.item_width  *
                    fridge_item.item_height *
                    fridge_item.quantity
                )

            #look up this user’s per-family limit
            try:
                tag = models.FamilyTag.objects.get(user=request.user, family=family)
                limit_fraction = tag.limit_ratio
                #no Limit for family owner
                if family.owner == request.user: 
                    limit_fraction = None
            except models.FamilyTag.DoesNotExist:
                limit_fraction = None

            #check user limit
            if limit_fraction is not None:
                existing_vol = Decimal('0')
                for ci in models.FridgeContent.items_added_by(request.user, family):
                    existing_vol += (
                        ci.item_length *
                        ci.item_width  *
                        ci.item_height
                    )
                
                total_volume = family.total_volume

                #if they’d exceed their allowed fraction, error out
                if (existing_vol + new_vol) > (total_volume * Decimal(limit_fraction)):
                    form.add_error(
                        None,
                        "Adding this item would exceed your allotted capacity "
                        f"({limit_fraction*100:.0f}% of {total_volume})."
                    )
                    return render(request, 'add_fridge_item.html',{'form': form})

                
            #check compartment limit

            compartment = fridge_item.compartment_id
            compartment_vol = (compartment.compartment_length * 
                               compartment.compartment_width * 
                               compartment.compartment_height )
            
            compartment_occupied = Decimal('0')
            for ci in models.FridgeContent.items_added_in(compartment, family):
                    compartment_occupied += (
                        ci.item_length *
                        ci.item_width  *
                        ci.item_height
                    )
            if (compartment_occupied + new_vol) > compartment_vol:
                    form.add_error(
                        None,
                        f"Adding this item would exceed the {compartment.compartment_name}'s capacity "
                        f"({compartment_occupied + new_vol} of {compartment_vol})."
                    )
                    return render(request, 'add_fridge_item.html',{'form': form})
                
            #passed the limit check, now save and redirect
            fridge_item.save()
            messages.success(request, "Item added successfully!")
            return redirect('fridgePage', family_id=family_id)
    else:
        form = FridgeContentForm(family=family)

    return render(request,'add_fridge_item.html',{'form': form})