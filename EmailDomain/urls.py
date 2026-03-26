from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.list_email_domains, name="list_email_domains"),
    path("create/", views.create_email_domain, name="create_email_domain"),
    path("<int:pk>/update/", views.update_email_domain, name="update_email_domain"),
    path("<int:pk>/delete/", views.delete_email_domain, name="delete_email_domain"),
]
