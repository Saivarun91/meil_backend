from django.db import models
from django.conf import settings
from django.utils import timezone
from Employee.models import Employee


class Permission(models.Model):
    permission_id = models.AutoField(primary_key=True)  # Internal generated
    permission_name = models.CharField(max_length=100, unique=True)  # VARCHAR
    permission_description = models.TextField(null=True, blank=True)  # VARCHAR
    template_role = models.JSONField(null=True, blank=True)  # JSONB

    created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(
        Employee,
        related_name="permission_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(
        Employee,
        related_name="permission_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def _str_(self):
        return self.permission_name