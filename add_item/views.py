from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemForm
from django.contrib import messages
from inventory.models import FridgeContent, FridgeDetail, ItemsDetails, CompartmentsDetails
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def add_item(request):
    family = request.user.family_set.first() 
    fridge = FridgeDetail.objects.get(family_id=family) 
    compartments = CompartmentsDetails.objects.filter(family_id=family)
    total_items = FridgeContent.objects.filter(family_id=family).count() 
    today = date.today()

    if total_items >= fridge.capacity:  
        messages.error(request, "Your fridge is full. Please remove an item before adding more.")
        return redirect('home')  

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.family_id = family
            new_item.save()
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = ItemForm()

    return render(request, "additem.html", {"form": form, "today": today, "compartments":compartments,})


@csrf_exempt
def update_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = ItemsDetails.objects.get(item_name=item_id)  
            item.item_name = data.get('item_name', item.item_name)
            item.item_description = data.get('item_description', item.item_description)
            item.item_expiration = data.get('item_expiration', item.item_expiration)
            item.save()
            return JsonResponse({'success': True})
        except ItemsDetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


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
    # gets all availble items in the database
    items = ItemsDetails.objects.all()
    return render(request, 'unregisteritem.html', {'items': items})

@csrf_exempt
def remove_fridge_item(request, item_id):
    if request.method == 'DELETE':
        try:
            location = request.GET.get('location')  # Get location from query parameters

            if not location:
                return JsonResponse({'success': False, 'error': 'Location is required.'}, status=400)

            # gets item ID and location
            fridge_item = get_object_or_404(FridgeContent, item_id=item_id, location=location)
            fridge_item.delete()  # deletes it

            return JsonResponse({'success': True, 'message': 'Fridge item removed successfully.'})
        except FridgeContent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found in the specified location.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@csrf_exempt
def remove_item(request, item_id):
    if request.method == 'DELETE':
        try:
            item = get_object_or_404(ItemsDetails, item_name=item_id)
            item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

