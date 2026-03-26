from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_permissions, name="list_permissions"),
    path("create/", views.create_permission_for_role, name="create_permission"),
    path("<int:pk>/", views.permission_detail, name="permission_detail"),
]
