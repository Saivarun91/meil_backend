from django.contrib import admin
from .models import SignupRequest

@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "description", "is_approved", "created")
    list_filter = ("is_approved", "created")
    search_fields = ("email", "description")
    ordering = ("-created",)
