from django.urls import path
from . import views

urlpatterns = [
    path('roles/', views.userrole_list, name='userrole_list'),
    path('roles/create/', views.userrole_create, name='userrole_create'),
    path('roles/permissions/update/', views.bulk_update_role_permissions,
         name='bulk_update_role_permissions'),  # ✅ New endpoint
    path('roles/permissions/assign/', views.assign_role_permissions,
         name='assign_role_permissions'),
    path('roles/permissions/remove/', views.remove_role_permission,
         name='remove_role_permission'),

    path('roles/update/<int:pk>/', views.userrole_update, name='userrole_update'),
    path('roles/delete/<int:pk>/', views.userrole_delete, name='userrole_delete'),
    path('roles/permissions/<str:role_name>/',
         views.userrole_permissions, name='userrole_permissions'),
    path('roles/all/', views.all_roles_with_permissions,
         name='all_roles_with_permissions'),


]