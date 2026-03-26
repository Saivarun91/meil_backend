from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_matgattribute, name='create_matgattribute'),
    path('list/', views.list_matgattributes, name='list_matgattributes'),

    # Update a single attribute row
    path('update/<int:item_id>/', views.update_matgattribute, name='update_matgattribute'),

    # Delete a single attribute row
    path('delete/<int:item_id>/', views.delete_matgattribute, name='delete_matgattribute'),
]
