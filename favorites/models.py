from django.db import models
from django.utils import timezone
from Employee.models import Employee
from itemmaster.models import ItemMaster
from matgroups.models import MatGroup


class Favorite(models.Model):
    """
    Model to store user's favorite materials (material groups)
    """
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="favorites",
        null=False
    )
    mgrp_code = models.ForeignKey(
        MatGroup,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        to_field="mgrp_code",
        null=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("employee", "mgrp_code")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.employee.emp_name} - {self.mgrp_code.mgrp_code}"


