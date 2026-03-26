
# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# class MaterialType(models.Model):
#     mat_type_code = models.CharField(max_length=4, primary_key=True)  # PK (char 4)
#     mat_type_desc = models.CharField(max_length=100)

#     # Audit fields
#     created = models.DateTimeField(default=timezone.now)
#     createdby = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="materialtype_created",
#         on_delete=models.SET_NULL,
#         null=True, blank=True
#     )
#     updated = models.DateTimeField(default=timezone.now)  
#     updatedby = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="materialtype_updated",
#         on_delete=models.SET_NULL,
#         null=True, blank=True
#     )
#     is_deleted = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.mat_type_code} - {self.mat_type_desc}"
from django.db import models
from django.conf import settings
from django.utils import timezone
from Employee.models import Employee

class MaterialType(models.Model):
    mat_type_code = models.CharField(max_length=4, primary_key=True)  # PK (char 4)
    mat_type_desc = models.CharField(max_length=100)

    # Audit fields
    created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(
        Employee,
        related_name="materialtype_created",
        on_delete=models.CASCADE,  # ✅ Cascade delete when user is deleted
        null=True, blank=True
    )
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(
        Employee,
        related_name="materialtype_updated",
        on_delete=models.CASCADE,  # ✅ Cascade delete when user is deleted
        null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mat_type_code} - {self.mat_type_desc}"
