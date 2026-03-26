from django.urls import path
from . import views

urlpatterns = [
    path("validation-lists/", views.validation_list_all, name="validation_list_all"),
    path("validation-lists/create/", views.validation_list_create, name="validation_list_create"),
    path("validation-lists/<int:list_id>/update/", views.validation_list_update, name="validation_list_update"),
    path("validation-lists/<int:list_id>/delete/", views.validation_list_delete, name="validation_list_delete"),
]

