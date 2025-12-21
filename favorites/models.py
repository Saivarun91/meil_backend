from django.db import models
from django.utils import timezone
from Employee.models import Employee
from itemmaster.models import ItemMaster
from matgroups.models import MatGroup


class Favorite(models.Model):
    """
    Model to store user's favorite materials (items only)
    """
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="favorites",
        null=False
    )
    # Item/material favorite (required)
    item = models.ForeignKey(
        ItemMaster,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        null=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]
        unique_together = ("employee", "item")

    def __str__(self):
        return f"{self.employee.emp_name} - Item {self.item.local_item_id}"


class SharedMaterial(models.Model):
    """
    Model to store shared materials between users
    """
    id = models.AutoField(primary_key=True)
    shared_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="shared_materials",
        null=False
    )
    shared_with = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="received_materials",
        null=False
    )
    item = models.ForeignKey(
        ItemMaster,
        on_delete=models.CASCADE,
        related_name="shared_with_users",
        null=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]
        unique_together = ("shared_by", "shared_with", "item")

    def __str__(self):
        return f"{self.shared_by.emp_name} shared Item {self.item.local_item_id} with {self.shared_with.emp_name}"
