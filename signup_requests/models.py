# Approvals/models.py
from django.db import models
from django.utils import timezone
from Company.models import Company


class SignupRequest(models.Model):
    emp_name = models.CharField(
        max_length=255, null=True, blank=True, default="Unknown")

    email = models.EmailField(unique=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="signup_requests", null=True, blank=True
    )
    # ⚠️ will be hashed later when creating Employee
    password = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.emp_name} ({self.email})"
