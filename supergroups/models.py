from django.db import models
from django.conf import settings
from django.utils import timezone
from Employee.models import Employee
class SuperGroup(models.Model):
    sgrp_code = models.CharField(max_length=5, primary_key=True)
    sgrp_name = models.CharField(max_length=100)
    dept_name = models.CharField(max_length=20)
    # Audit fields
    created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(Employee, related_name="supergroup_created",
                                  on_delete=models.SET_NULL, null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(Employee, related_name="supergroup_updated",
                                  on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.sgrp_name