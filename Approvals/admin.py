from django.contrib import admin
from .models import Approval


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role_assigned")
    search_fields = ("email", "role_assigned")
    list_filter = ("role_assigned",)
