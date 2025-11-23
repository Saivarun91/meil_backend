
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from signup_requests.models import SignupRequest
from Employee.models import Employee
from Users.models import UserRole
from Company.models import Company
from .models import Approval
from Common.Middleware import authenticate, restrict


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin"])
def approve_user(request, signup_id):
    """
    Approve a pending signup request.
    POST /approval/<signup_id>/
    If employee exists -> update role, password, and company
    If not -> create new employee
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        signup_request = SignupRequest.objects.get(
            id=signup_id, is_approved=False)
    except SignupRequest.DoesNotExist:
        return JsonResponse(
            {"error": "Signup request not found or already approved"},
            status=404
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    password = data.get("password")
    role_assigned = data.get("role_assigned")
    company_name = data.get("company_name")

    if not (password and role_assigned):
        return JsonResponse(
            {"error": "password and role_assigned are required"},
            status=400
        )

    # ✅ Check role
    try:
        role = UserRole.objects.get(role_name=role_assigned)
    except UserRole.DoesNotExist:
        return JsonResponse({"error": "Role not found"}, status=404)

    # ✅ Company required if not SuperAdmin
    company = None
    if role_assigned.lower() != "superadmin":
        if not company_name:
            return JsonResponse(
                {"error": "company_name is required for this role"},
                status=400
            )
        try:
            company = Company.objects.get(company_name=company_name)
        except Company.DoesNotExist:
            return JsonResponse({"error": "Company not found"}, status=404)

    # ✅ Create or Update Employee
    employee, created = Employee.objects.get_or_create(
        email=signup_request.email,
        defaults={
            "password": make_password(password),
            "role": role,
            "company_name": company
        }
    )

    if not created:
        # Update existing employee’s role, password, company
        employee.password = make_password(password)
        employee.role = role
        employee.company_name = company
        employee.save()

    # ✅ Mark approved
    signup_request.is_approved = True
    signup_request.save()

    # ✅ Update or create Approval record
    approval, _ = Approval.objects.update_or_create(
        email=signup_request.email,
        defaults={
            "role_assigned": role.role_name,
            "company": company
        }
    )

    return JsonResponse({
        "message": "User approved successfully" if created else "User updated successfully",
        "employee": {
            "emp_id": employee.emp_id,
            "email": employee.email,
            "role": role.role_name,
            "company": company.company_name if company else None
        }
    }, status=201 if created else 200)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin"])
def get_user(request, approval_id):
    """
    Get details of a specific approved user.
    GET /approval/user/<approval_id>/
    """
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        approval = Approval.objects.get(id=approval_id)
    except Approval.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({
        "email": approval.email,
        "role": approval.role_assigned,
        "company": approval.company.company_name if approval.company else None
    }, status=200)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin"])
def get_all_users(request):
    """
    Get list of all approved users.
    GET /approval/users/
    """
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    approvals = Approval.objects.all()
    data = [
        {
            "email": a.email,
            "role": a.role_assigned,
            "company": a.company.company_name if a.company else None
        } for a in approvals
    ]
    return JsonResponse(data, safe=False, status=200)
