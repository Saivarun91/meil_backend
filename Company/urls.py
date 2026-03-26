 # Create a new company

from django.urls import path
from . import views

urlpatterns = [
    path("companies/", views.list_companies),
    path("companies/public/", views.list_companies_public),  # Public endpoint for registration
    path("companies/create/", views.create_company),
    path("companies/update/<str:company_name>/", views.update_company),
    path("companies/delete/<str:company_name>/", views.delete_company),
]


