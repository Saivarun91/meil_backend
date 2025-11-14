from django.db import models
from Employee.models import Employee


class MatgAttributeItem(models.Model):
    id = models.AutoField(primary_key=True)
    mgrp_code = models.ForeignKey(
        "matgroups.MatGroup",
        on_delete=models.CASCADE,
        related_name="attributes_items"
    )

    # Attribute name
    attribute_name = models.CharField(max_length=150)

    # All possible options for this attribute (dropdown values)
    possible_values = models.JSONField(
        default=list,
        help_text="Fixed allowed values for this attribute"
    )

    # Optional: Unit of Measure (for numeric style attributes)
    uom = models.CharField(
        max_length=50,
        null=True, blank=True,
        help_text="UOM for numeric dropdown attributes (optional)"
    )

    # Optional sorting priority
    print_priority = models.IntegerField(null=True, blank=True)

    # Optional validation if needed
    validation = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(
        Employee, related_name="matgitem_created",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    updated = models.DateTimeField(auto_now=True)
    updatedby = models.ForeignKey(
        Employee, related_name="matgitem_updated",
        on_delete=models.SET_NULL, null=True, blank=True
    )

    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("mgrp_code", "attribute_name")

    def __str__(self):
        return f"{self.attribute_name} (@{self.mgrp_code_id})"
