# from django.db import models
# from django.conf import settings
# from django.utils import timezone


# class Project(models.Model):
#     project_code = models.IntegerField(primary_key=True)  # 3 or 4 digit number
#     project_name = models.CharField(max_length=50, unique=True)

#     # ALLTABLES audit columns
#     created = models.DateTimeField(default=timezone.now)  # timestamp
#     createdby = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="project_created",
#         on_delete=models.SET_NULL,
#         null=True, blank=True
#     )
#     updated = models.DateTimeField(default=timezone.now)  # timestamp
#     updatedby = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="project_updated",
#         on_delete=models.SET_NULL,
#         null=True, blank=True
#     )
#     is_deleted = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.project_code} - {self.project_name}"
from django.db import models
from django.utils import timezone

class Project(models.Model):
    project_code = models.CharField(max_length=50, primary_key=True)
    project_name = models.CharField(max_length=255)

    # ALLTABLES audit columns
    created = models.DateTimeField(default=timezone.now)  # timestamp
    createdby = models.ForeignKey(
        "Employee.Employee",
        on_delete=models.CASCADE,
        related_name="projects_created",
        null=True, blank=True
    )
    updated = models.DateTimeField(default=timezone.now)  # timestamp
    updatedby = models.ForeignKey(
        "Employee.Employee",
        on_delete=models.CASCADE,
        related_name="projects_updated",
        null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        
        return f"{self.project_code} - {self.project_name}"


