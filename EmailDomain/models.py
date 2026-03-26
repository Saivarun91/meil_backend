from django.db import models
from django.utils import timezone
from Employee.models import Employee  # link directly to Employee

class EmailDomain(models.Model):
    emaildomain_id = models.AutoField(primary_key=True)
    domain_name = models.CharField(max_length=255, unique=True)

    # Audit fields
    created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(
        Employee,
        related_name="emaildomain_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(
        Employee,
        related_name="emaildomain_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.domain_name
