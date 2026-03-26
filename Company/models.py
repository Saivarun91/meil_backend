from django.db import models
from django.conf import settings
from django.utils import timezone

class Company(models.Model):
    company_name = models.CharField(max_length=20, primary_key=True)  # PK (varchar 20)
    contact = models.CharField(max_length=20, null=True, blank=True)
    # Audit fields
    created = models.DateTimeField(default=timezone.now)  # record created timestamp
    createdby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="company_created",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    updated = models.DateTimeField(default=timezone.now)   # auto-update timestamp
    updatedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="company_updated",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name
