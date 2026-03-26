# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# class UserRole(models.Model):
#     userrole_id = models.AutoField(primary_key=True)  # autonumber
#     role_name = models.CharField(max_length=10, unique=True,null=True,blank=True)  # ADMIN, SUPERADMIN, USER, MDGT
#     role_priority = models.IntegerField(null=True,blank=True)  # higher number = more privileges

#     created = models.DateTimeField(default=timezone.now)   # record created timestamp
#     createdby = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="userrole_created",
#         on_delete=models.SET_NULL,
#         null=True, blank=True
#     )
#     updated = models.DateTimeField(default=timezone.now)       # record last updated timestamp
#     updatedby = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="userrole_updated",
#         on_delete=models.SET_NULL,
#         null=True, blank=True
#     )
#     is_deleted = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.role_name} (Priority {self.role_priority})"

from django.db import models
from django.conf import settings
from django.utils import timezone


class UserRole(models.Model):
    userrole_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=10, null=True, blank=True)
    role_priority = models.IntegerField(null=True, blank=True)

    permission = models.ForeignKey(
        "permissions.Permission",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles"
    )

    # CRUD + Export booleans
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)

    created = models.DateTimeField(default=timezone.now,null=True)
    createdby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="userrole_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_emp_id = models.IntegerField(
        null=True, blank=True)  # ✅ New field for JWT user ID
    updated = models.DateTimeField(default=timezone.now,null=True)
    updatedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="userrole_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_emp_id = models.IntegerField(
        null=True, blank=True)  # ✅ New field for JWT user ID
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.role_name
