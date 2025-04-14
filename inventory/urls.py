from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.loginPage, name='LoginPage'),
    path('', views.heroPage, name='heroPage'),
    path("home/", views.home, name="home"),
    path("fridgePage/", views.fridgePage, name="fridgePage"),
    path("logout/", views.logoutUser, name='logout'),
    path("addFridge/", views.addFridge, name='addFridge'),

]