from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_matgroups, name='list_matgroups'),  # GET all MatGroups
    path('create/', views.create_matgroup, name='create_matgroup'),  # POST create MatGroup
    path('<str:mgrp_code>/update/', views.update_matgroup, name='update_matgroup'),  # PUT update MatGroup
    path('<str:mgrp_code>/delete/', views.delete_matgroup, name='delete_matgroup'),  # DELETE MatGroup
]
