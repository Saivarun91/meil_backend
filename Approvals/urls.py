from django.urls import path
from .views import approve_user, get_user, get_all_users

urlpatterns = [
    path("approval/<int:signup_id>/", approve_user, name="approve-user"),
    path("approval/user/<int:approval_id>/", get_user, name="user-detail"),
    path("approval/users/", get_all_users, name="user-list"),
]

