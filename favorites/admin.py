from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "mgrp_code", "created", "is_deleted")
    list_filter = ("is_deleted", "created")
    search_fields = ("employee__emp_name", "mgrp_code__mgrp_code", "mgrp_code__mgrp_shortname")
    readonly_fields = ("created", "updated")


