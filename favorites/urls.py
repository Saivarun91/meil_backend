from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_favorite, name="add_favorite"),
    path("remove/<int:favorite_id>/", views.remove_favorite, name="remove_favorite"),
    path("remove/", views.remove_favorite, name="remove_favorite_by_code"),
    path("list/", views.list_favorites, name="list_favorites"),
]


