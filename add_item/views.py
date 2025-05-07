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
        form = FridgeContentForm(request.POST, family=family)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.family_id = get_object_or_404(Family, pk=family_id)
            fridge_item.user = request.user
            
            item: ItemsDetails = form.cleaned_data['item_id']
            fridge_item.item_length = item.dimension_length
            fridge_item.item_width = item.dimension_width
            fridge_item.item_height = item.dimension_height
            fridge_item.compartment_id = form.cleaned_data['compartment_id']
            new_vol = (
                    fridge_item.item_length *
                    fridge_item.item_width  *
                    fridge_item.item_height *
                    fridge_item.quantity
                )

            # Set the default description from ItemsDetails
            fridge_item.item_description = item.item_description

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
            family_id = data.get('family_id')
            compartment_id = data.get('compartment_id')

            if not family_id or not compartment_id:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

            # Get the fridge item
            fridge_item = get_object_or_404(
                FridgeContent,
                item_id=item_id,
                family_id=family_id,
                compartment_id=compartment_id
            )

            

            # Update the FridgeContent object
            fridge_item.item_description = data.get('item_description')
            fridge_item.expiration_date = data.get('item_expiration')
            fridge_item.quantity = data.get('item_count')
            fridge_item.save() 

            # Recalculate the occupied volume for the compartment
            compartment = fridge_item.compartment_id
            occupied = compartment.occupied

            return JsonResponse({'success': True, 'new_count': fridge_item.quantity, 'occupied': occupied})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@csrf_exempt
def remove_item(request, item_id):
    if request.method == 'DELETE':
        family_id = request.GET.get('family_id')
        compartment_id = request.GET.get('compartment_id')

        if not family_id or not compartment_id:
            return JsonResponse({'success': False, 'error': 'Family ID and compartment ID are required.'}, status=400)

        try:
            # Find and delete the specific fridge content
            fridge_item = get_object_or_404(
                FridgeContent,
                item_id=item_id,
                family_id=family_id,
                compartment_id=compartment_id
            )
            fridge_item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed successfully.'})
        except FridgeContent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found in the specified fridge and compartment.'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

