from datetime import date
from django.shortcuts import render, redirect
from .forms import ItemForm
from django.contrib import messages
from inventory.models import FridgeContent, FridgeDetail, ItemsDetails
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def add_item(request):
    family = request.user.family_set.first() 
    fridge = FridgeDetail.objects.get(family_id=family)  
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

            FridgeContent.objects.create(
                expiration_date = new_item.item_expiration,
                family_id = family,
                compartment_id = family.CompartmentsDetails.get(compartment_name = new_item.item_type),
                item_id = new_item,
                item_length = new_item.dimension_length,
                item_width = new_item.dimension_width,
                item_height = new_item.dimension_height,
                added_date = today
            )

            return redirect('home')
    else:
        form = ItemForm()

    return render(request, "additem.html", {"form": form, "today": today})



@csrf_exempt
def update_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = ItemsDetails.objects.get(item_id=item_id)  # Use `item_id` as the primary key
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
