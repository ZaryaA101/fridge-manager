from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from inventory.forms import FridgeContentForm
from django.contrib import messages
from inventory.models import *
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

def add_item(request, family_id):
    family = get_object_or_404(Family, pk=family_id)

    if request.method == "POST":
        form = FridgeContentForm(request.POST)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.family_id = family
            fridge_item.user = request.user
            
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
                tag = FamilyTag.objects.get(user=request.user, family=family)
                limit_fraction = tag.limit_ratio
                #no Limit for family owner
                if family.owner == request.user: 
                    limit_fraction = None
            except FamilyTag.DoesNotExist:
                limit_fraction = None

            #check user limit
            if limit_fraction is not None:
                existing_vol = Decimal('0')
                for ci in FridgeContent.items_added_by(request.user, family):
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
                    return render(request, 'addItem.html',{'form': form})

                
            #check compartment limit

            compartment = fridge_item.compartment_id
            compartment_vol = (compartment.compartment_length * 
                               compartment.compartment_width * 
                               compartment.compartment_height )
            
            compartment_occupied = Decimal('0')
            for ci in FridgeContent.items_added_in(compartment, family):
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
                    return render(request, 'addItem.html',{'form': form})
                
            #passed the limit check, now save and redirect
            fridge_item.save()
            messages.success(request, "Item added successfully!")
            return redirect('fridgePage', family_id=family_id)
    else:
        form = FridgeContentForm(family=family)

    return render(request,'addItem.html',{'form': form})

@csrf_exempt
def update_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = ItemsDetails.objects.get(item_id=item_id)
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
def remove_item(request, item_id):
    print(f"Request method: {request.method}")  # Debugging stuff
    if request.method == 'DELETE':
        fridge_id = request.GET.get('family_id')
        location = request.GET.get('location')

        if not fridge_id or not location:
            return JsonResponse({'success': False, 'error': 'Fridge ID and location are required.'}, status=400)

        try:
            fridge_item = get_object_or_404(
                FridgeContent,
                item_id=item_id,
                family_id=fridge_id,
                location=location
            )
            fridge_item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed successfully.'})
        except FridgeContent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found in the specified fridge and location.'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)
