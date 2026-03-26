from django.urls import path
from .views import SignupRequestView, get_pending_signups

urlpatterns = [
    path("signup/", SignupRequestView.as_view(), name="signup_request"),
    path("signup/pending/", get_pending_signups, name="get_pending_signups"),
]
