from django.db import models
from django.conf import settings
from django.utils import timezone
from Employee.models import Employee


class ValidationLists(models.Model):
    list_id = models.AutoField(primary_key=True)
    listname = models.CharField(max_length=20)
    listvalue = models.JSONField()   # ✅ Changed to JSONField

    created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(
        Employee,
        related_name="validationlist_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(
        Employee,
        related_name="validationlist_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.listname} - {self.listvalue}"
