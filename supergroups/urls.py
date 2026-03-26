from django.urls import path
from . import views

urlpatterns = [
    path('supergroups/create/', views.create_supergroup, name='create_supergroup'),
    path('supergroups/list/', views.list_supergroups, name='list_supergroups'),
    path('supergroups/update/<str:sgrp_code>/', views.update_supergroup, name='update_supergroup'),
    path('supergroups/delete/<str:sgrp_code>/', views.delete_supergroup, name='delete_supergroup'),
]
