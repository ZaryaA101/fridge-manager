from django.urls import path
from . import views

urlpatterns = [
    path('family/<uuid:family_id>/add_item/', views.add_item, name='add_item'),
    path('remove-item/<str:item_id>/', views.remove_item, name='remove_item'),
    path('update-item/<str:item_id>/', views.update_item, name='update_item'),  
]
