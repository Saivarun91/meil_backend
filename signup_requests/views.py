# signup_requests/views.py
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password

from .models import SignupRequest
from Employee.models import Employee
from Company.models import Company
# adjust import path if needed
from Common.Middleware import authenticate, restrict


class SignupRequestView(APIView):
    permission_classes = [AllowAny]   # 👈 public signup

    def post(self, request):
        emp_name = request.data.get("emp_name")
        email = request.data.get("email")
        company_name = request.data.get("company_name")
        password = request.data.get("password")

        if not emp_name or not email or not company_name or not password:
            return Response(
                {"error": "emp_name, email, company_name, and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if SignupRequest.objects.filter(email=email).exists() or Employee.objects.filter(email=email, is_deleted=False).exists():
            return Response(
                {"error": "Email already registered/requested"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find company
        try:
            company = Company.objects.get(company_name=company_name)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create signup request
        signup_request = SignupRequest.objects.create(
            emp_name=emp_name,
            email=email,
            company=company,
            password=make_password(password),
            description=f"Signup request for {emp_name} at {company.company_name}"
        )

        # Also create Employee directly (but not yet approved)
        employee = Employee.objects.create(
            emp_name=emp_name,
            email=email,
            password=signup_request.password,  # already hashed
            company_name=company
        )

        return Response({
            "message": "Signup request submitted & employee created",
            "signup_id": signup_request.id,
            "emp_id": employee.emp_id,
            "email": employee.email,
            "company": company.company_name
        }, status=status.HTTP_201_CREATED)


# 🔹 New protected view for pending signups
@authenticate
# @restrict(["Admin", "SuperAdmin"])   # ✅ only admins can fetch pending requests
def get_pending_signups(request):
    pending_requests = SignupRequest.objects.filter(is_approved=False).values(
        "id", "emp_name", "email", "company__company_name", "created"
    )
    return JsonResponse(list(pending_requests), safe=False, status=200)
