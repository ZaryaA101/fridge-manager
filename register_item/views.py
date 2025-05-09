from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm
from django.contrib import messages
from inventory.models import FridgeContent, FridgeDetail, ItemsDetails, CompartmentsDetails

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def register_item(request):
    family = request.user.family_set.first() 
    fridge = FridgeDetail.objects.get(family_id=family) 
    compartments = CompartmentsDetails.objects.filter(family_id=family)
    total_items = FridgeContent.objects.filter(family_id=family).count() 
    today = date.today()
    #check if the current user is the owner of the family
    if family.owner == request.user:
        is_owner = True
    else:
        is_owner = False

    #if total_items >= fridge.capacity:  
    #    messages.error(request, "Your fridge is full. Please remove an item before adding more.")
    #    return redirect('home')  

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():

            # Check if the item already exists in the database
            item_name = form.cleaned_data['item_name']  
            existing_item = ItemsDetails.objects.filter(item_name__iexact=item_name).first() 
            if existing_item:
                messages.error(request, f"The item '{item_name}' is already registered in the item registry.")
                return render(request, "registerItem.html", {"form": form, "today": today, "compartments": compartments,"is_owner": is_owner})
        
            #save the new item
            new_item = form.save(commit=False)
            new_item.family_id = family
            new_item.save()
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = ItemForm()

    return render(request, "registerItem.html", {"form": form, "today": today, "compartments":compartments,"is_owner": is_owner})



@csrf_exempt
def unregister_item(request):
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')  # Get item_id from the form
        try:
            # get and delete the item using item_id
            item = get_object_or_404(ItemsDetails, item_id=item_id)
            item.delete()
            messages.success(request, f"Item '{item.item_name}' has been unregistered successfully.")
        except ItemsDetails.DoesNotExist:
            messages.error(request, "The selected item does not exist.")
        except Exception as e:
            messages.error(request, "An error occurred while trying to unregister the item.")
        return redirect('unregister_item_page')
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def unregister_item_page(request):
    family = request.user.family_set.first()
    #check if the current user is the owner of the family
    if family.owner == request.user:
        is_owner = True
    else:
        is_owner = False
    # gets all availble items in the database
    items = ItemsDetails.objects.all()
    return render(request, 'unregisteritem.html', {'items': items, 'is_owner': is_owner})

