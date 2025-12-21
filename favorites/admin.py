from django.contrib import admin
from .models import Favorite, SharedMaterial


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "get_item_info", "created", "is_deleted")
    list_filter = ("is_deleted", "created")
    search_fields = ("employee__emp_name", "item__short_name",
                     "item__mgrp_code__mgrp_code")
    readonly_fields = ("created", "updated")

    def get_item_info(self, obj):
        if obj.item:
            return f"{obj.item.short_name} (ID: {obj.item.local_item_id})"
        return "-"
    get_item_info.short_description = "Item"


@admin.register(SharedMaterial)
class SharedMaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "shared_by", "shared_with",
                    "get_item_info", "created", "is_deleted")
    list_filter = ("is_deleted", "created")
    search_fields = ("shared_by__emp_name",
                     "shared_with__emp_name", "item__short_name")
    readonly_fields = ("created", "updated")

    def get_item_info(self, obj):
        if obj.item:
            return f"{obj.item.short_name} (ID: {obj.item.local_item_id})"
        return "-"
    get_item_info.short_description = "Item"
