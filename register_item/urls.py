from django.urls import path
from . import views

urlpatterns = [
    path('register-item', views.register_item, name='register_item'),
    #path('update-item/<str:item_id>/', views.update_item, name='update_item'),
    #path('remove-item/<str:item_id>/', views.remove_item, name='remove_item'),
    #path('remove-fridge-item/<str:item_id>/', views.remove_fridge_item, name='remove_fridge_item'),
    path('unregister-item/', views.unregister_item_page, name='unregister_item_page'),
    path('unregister-item/submit/', views.unregister_item, name='unregister_item'),
]
