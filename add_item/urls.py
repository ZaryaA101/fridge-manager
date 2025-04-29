from django.urls import path
from . import views

urlpatterns = [
    path('additem', views.add_item, name='add_item'),
    path('update-item/<uuid:item_id>/', views.update_item, name='update_item'),
    path('remove-item/<uuid:item_id>/', views.remove_item, name='remove_item'),
    path('remove-fridge-item/<uuid:item_id>/', views.remove_fridge_item, name='remove_fridge_item'),

    path('unregister-item/', views.unregister_item_page, name='unregister_item_page'),
    path('unregister-item/submit/', views.unregister_item, name='unregister_item'),
]
