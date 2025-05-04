from django.urls import path
from . import views

urlpatterns = [
    path('register-item', views.register_item, name='register_item'),
    path('unregister-item/', views.unregister_item_page, name='unregister_item_page'),
    path('unregister-item/submit/', views.unregister_item, name='unregister_item'),
]
