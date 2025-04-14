from django.urls import path
from . import views

urlpatterns = [
    path('additem', views.add_item, name='add_item'),
]