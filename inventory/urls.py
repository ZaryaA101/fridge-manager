from django.urls import path
from add_item.views import update_item, remove_item, remove_fridge_item, unregister_item, unregister_item_page

from . import views

urlpatterns = [
    path('login/', views.loginPage, name='LoginPage'),
    path('', views.heroPage, name='heroPage'),
    path("home/", views.home, name="home"),
    #path("fridgePage/", views.fridgePage, name="fridgePage"),
    path('family/<uuid:family_id>/fridgePage/', views.fridgePage, name='fridgePage'),
    path("logout/", views.logoutUser, name='logout'),
    path("addFridge/", views.addFridge, name='addFridge'),
    path("profilePage/", views.profilePage, name="profilePage"),
    path("createFamily/", views.createFamily, name="createFamily"),
    path('family/<uuid:family_id>/manage_members/', views.manageFamilyMembers, name='manageFamilyMembers'),
    path('my_families/', views.my_families, name='my_families'),
    path('family/<uuid:family_id>/manage_fridge/', views.manage_fridge_details, name='manage_fridge_details'),
    path('family/<uuid:family_id>/add_fridge_item/', views.add_fridge_item, name='add_fridge_item'),

    path('update-item/<str:item_id>/', update_item, name='update_item'),
    path('remove-item/<str:item_id>/', remove_item, name='remove_item'),
    path('remove-fridge-item/<str:item_id>/', remove_fridge_item, name='remove_fridge_item'),

    path('unregister-item/', unregister_item_page, name='unregister_item_page'),
    path('unregister-item/submit/', unregister_item, name='unregister_item'),
]
