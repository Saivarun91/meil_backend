 
from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.list_projects, name="list_projects"),
    path("create/", views.create_project, name="create_project"),
    path('<str:pk>/update/', views.update_project, name='update_project'),
    path("<str:pk>/delete/", views.delete_project, name="delete_project"),
]
