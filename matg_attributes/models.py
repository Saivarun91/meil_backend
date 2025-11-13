from django.db import models
from django.utils import timezone
from Employee.models import Employee


class MatgAttribute(models.Model):
    attrib_id = models.AutoField(primary_key=True)
    mgrp_code = models.ForeignKey(
        "matgroups.MatGroup",
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    # ✅ JSONB field for storing flexible attribute/value mappings
    # Example:
    # {
    #   "Color": {
    #       "values": ["Red", "Blue", "Green"],
    #       "print_priority": 1,
    #       "validation": "alpha",
    #       "max_length": 10
    #   },
    #   "Size": {
    #       "values": ["S", "M", "L"],
    #       "print_priority": 2
    #   }
    # }
    attributes = models.JSONField(
        default=dict,
        help_text="JSON structure storing attribute names and their possible values"
    )

    # ✅ Audit fields
    created = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(
        Employee, related_name="matgattr_created",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(
        Employee, related_name="matgattr_updated",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Attributes for MatGroup {self.mgrp_code_id}"

    class Meta:
        verbose_name = "Material Group Attribute"
        verbose_name_plural = "Material Group Attributes"
