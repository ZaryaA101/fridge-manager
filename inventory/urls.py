from django.urls import path

from . import views

#app_name = 'inventory'
urlpatterns = [
    path('login/', views.loginPage, name='LoginPage'),
    path('', views.heroPage, name='heroPage'),
    path("home/", views.home, name="home"),
    path("logout/", views.logoutUser, name='logout'),

]