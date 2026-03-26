from django.urls import path
from . import views

urlpatterns = [
    path('materialtypes/', views.list_material_types),
    path('materialtypes/create/', views.create_material_type),
    path('materialtypes/update/<str:mat_type_code>/', views.update_material_type),
    path('materialtypes/delete/<str:mat_type_code>/', views.delete_material_type),
]
