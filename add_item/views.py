from django.shortcuts import render, redirect
from .forms import ItemForm

def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ItemForm()
    return render(request, "additem.html", {"form": form})