from django.db import models
from django.utils import timezone


class Employee(models.Model):
    emp_id = models.AutoField(primary_key=True)
    emp_name = models.CharField(
        max_length=255, null=False, blank=False, default="Unknown")
    email = models.EmailField(
        max_length=100, null=False, blank=False)
    password = models.CharField(max_length=255)
    
    phone_number = models.CharField(max_length=15, null=True, blank=True)  
    designation = models.CharField(max_length=30, null=True, blank=True)
    company_name = models.ForeignKey(
        "Company.Company",
        on_delete=models.CASCADE,
        related_name="employees",
        null=True, blank=True
    )
    role = models.ForeignKey(
        "Users.UserRole",
        on_delete=models.CASCADE,
        related_name="employees",
        null=True, blank=True
    )

    description = models.TextField(null=True, blank=True)

    created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(
        "self",                # 👈 now references another Employee
        related_name="created_employees",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    updated = models.DateTimeField(default=timezone.now)
    updatedby = models.ForeignKey(
        "self",                # 👈 also references another Employee
        related_name="updated_employees",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    is_deleted = models.BooleanField(default=False)

    # 🔹 Email OTP fields
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    email_otp_created = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    # 🔹 Phone OTP fields
    # phone_otp = models.CharField(max_length=6, null=True, blank=True)
    # phone_otp_created = models.DateTimeField(null=True, blank=True)
    # is_phone_verified = models.BooleanField(default=False)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(is_deleted=False),
                name="unique_active_employee_email",
            )
        ]



    def __str__(self):
        return f"{self.emp_name} ({self.email})"
