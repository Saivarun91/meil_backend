from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_itemmaster, name='create_itemmaster'),
    path('list/', views.list_itemmasters, name='list_itemmasters'),
    path('update/<int:local_item_id>/', views.update_itemmaster, name='update_itemmaster'),
    path('delete/<int:local_item_id>/', views.delete_itemmaster, name='delete_itemmaster'),
]
