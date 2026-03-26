# from django.db import models
# from signup_requests.models import SignupRequest
# class Approval(models.Model):
#     signup_request = models.OneToOneField(
#         SignupRequest,
#         on_delete=models.CASCADE,
#         related_name="approval",
#         null=True,blank=True
#     )
#     email = models.EmailField(max_length=100, unique=True,null=True,blank=True)
#     password = models.CharField(max_length=128,null=True,blank=True)   # should be hashed in production
#     role_assigned = models.CharField(max_length=50,null=True,blank=True)
#     created = models.DateTimeField(auto_now_add=True)   # <-- make sure this is here!
#     def __str__(self):
#         return f"{self.email} ({self.role_assigned})"
from django.db import models
from signup_requests.models import SignupRequest
from Company.models import Company   # ✅ import Company

class Approval(models.Model):
    signup_request = models.OneToOneField(
        SignupRequest,
        on_delete=models.CASCADE,
        related_name="approval",
        null=True, blank=True
    )
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)   # should be hashed
    role_assigned = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(       # ✅ new field
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approvals"
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.role_assigned}) - {self.company.company_name if self.company else 'No Company'}"
