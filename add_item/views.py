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

            fridge_item.compartment_id = form.cleaned_data['compartment_id']
            item = form.cleaned_data['item_id']

            # Check if the item already exists in the compartment
            existing_item = FridgeContent.objects.filter(
                family_id=family,
                compartment_id=fridge_item.compartment_id,
                item_id=item
            ).first()

            if existing_item:
                messages.error(request, f"The item '{item.item_name}' already exists in the compartment '{fridge_item.compartment_id.compartment_name}'.")
                return render(request, 'addItem.html', {'form': form})

            #check here to see if item is actually having a volume
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
            item_count = data.get('item_count')

            if not family_id or not compartment_id:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

            if not isinstance(item_count, int) or item_count <= 0:
                return JsonResponse({'success': False, 'error': 'Invalid item count'}, status=400)

            fridge_item = get_object_or_404(
                FridgeContent,
                item_id=item_id,
                family_id=family_id,
                compartment_id=compartment_id
            )
            compartment = fridge_item.compartment_id

            # Calculate the item volume
            item_volume = fridge_item.item_length * fridge_item.item_width * fridge_item.item_height

            # Calculate the new occupied volume
            new_occupied = compartment.occupied + (item_count * item_volume) - (fridge_item.quantity * item_volume)

            if new_occupied > compartment.total_vol:
                return JsonResponse({'success': False, 'error': 'Updating item count will exceed compartment capacity.'}, status=400)

            # Update the FridgeContent object
            fridge_item.item_description = data.get('item_description')
            fridge_item.expiration_date = data.get('item_expiration')
            fridge_item.quantity = item_count
            fridge_item.save()

            # Recalculate the usage ratio dynamically
            usage_ratio = compartment.usage_ratio

            # Calculate updated fridge usage
            family = get_object_or_404(Family, pk=family_id)
            total_volume = family.total_volume
            occupied_volume = family.occupied_volume
            usage_percent = (occupied_volume / total_volume * 100) if total_volume > 0 else 0

            # Calculate user-space usage
            try:
                tag = FamilyTag.objects.get(user=request.user, family=family)
                if tag.limit_ratio and request.user != family.owner:
                    limit_fraction = tag.limit_ratio
                else:
                    limit_fraction = 1  
                user_limit_space = total_volume * limit_fraction
                user_occupied_volume = sum(
                    ci.item_length * ci.item_width * ci.item_height * ci.quantity
                    for ci in FridgeContent.items_added_by(request.user, family)
                )
                user_percent = (user_occupied_volume / user_limit_space * 100) if user_limit_space > 0 else 0
            except FamilyTag.DoesNotExist:
                user_limit_space = total_volume
                user_percent = (occupied_volume / total_volume * 100) if total_volume > 0 else 0


            return JsonResponse({
                'success': True,
                'new_count': fridge_item.quantity,
                'occupied': compartment.occupied,  
                'usage_ratio': usage_ratio,
                'total_volume': total_volume,
                'usage_percent': usage_percent,
                'user_percent': user_percent,
                'user_limit_space': user_limit_space
            })
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

            # Calculate updated fridge usage
            family = get_object_or_404(Family, pk=family_id)
            total_volume = family.total_volume
            occupied_volume = family.occupied_volume- (fridge_item.item_length * fridge_item.item_width * fridge_item.item_height * fridge_item.quantity)
            usage_percent = (occupied_volume / total_volume * 100) if total_volume > 0 else 0

            # Calculate user-space usage
            try:
                tag = FamilyTag.objects.get(user=request.user, family=family)
                if tag.limit_ratio and request.user != family.owner:
                    limit_fraction = tag.limit_ratio
                else:
                    limit_fraction = 1  
                user_limit_space = total_volume * limit_fraction
                user_occupied_volume = sum(
                    ci.item_length * ci.item_width * ci.item_height * ci.quantity
                    for ci in FridgeContent.items_added_by(request.user, family)
                )
                user_percent = (user_occupied_volume / user_limit_space * 100) if user_limit_space > 0 else 0
            except FamilyTag.DoesNotExist:
                user_limit_space = total_volume
                user_percent = (occupied_volume / total_volume * 100) if total_volume > 0 else 0
            return JsonResponse({
                'success': True,
                'message': 'Item removed successfully.',
                'occupied_volume': occupied_volume,
                'total_volume': total_volume,
                'usage_percent': usage_percent,
                'user_percent': user_percent,
                'user_limit_space': user_limit_space
            })
        except FridgeContent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found in the specified fridge and compartment.'}, status=404)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


