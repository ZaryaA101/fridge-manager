from django.urls import path

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
]