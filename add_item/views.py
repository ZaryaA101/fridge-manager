from datetime import date
from django.shortcuts import render, redirect
from .forms import ItemForm
from django.contrib import messages
from inventory.models import FridgeContent, FridgeDetail

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
           
            return redirect('home')
    else:
        form = ItemForm()

    return render(request, "additem.html", {"form": form, "today": today})
