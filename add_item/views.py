from django.shortcuts import render, redirect
from .forms import ItemForm
from django.contrib import messages
from .models import FridgeContent, FridgeDetail

def add_item(request):
    family = request.user.family_set.first()  # Get the family of the logged-in user
    fridge = FridgeDetail.objects.get(family_id=family)  # Get the fridge for the family
    total_items = FridgeContent.objects.filter(family_id=family).count()  # Total number of items

    if total_items >= fridge.capacity:  # Check if fridge is full
        messages.error(request, "Your fridge is full. Please remove an item before adding more.")
        return redirect('home')  # Redirect to home or any other page

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.family_id = family
            new_item.save()
            # Update fridge content count or other actions as needed
            return redirect('home')
    else:
        form = ItemForm()

    return render(request, "additem.html", {"form": form})
