from django.urls import path
from . import views

urlpatterns = [
    path('additem', views.add_item, name='add_item'),
    path('update-item/<uuid:item_id>/', views.update_item, name='update_item'),
]
