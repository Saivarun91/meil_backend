import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone

from Common.Middleware import authenticate, restrict
from .models import EmailDomain
from Employee.models import Employee


# Helper function
def is_admin_or_superadmin(user_payload):
    return user_payload.get("role") in ["Admin", "SuperAdmin"]


# List all email domains
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def list_email_domains(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    domains = EmailDomain.objects.filter(is_deleted=False)
    data = [
        {
            "emaildomain_id": d.emaildomain_id,
            "domain_name": d.domain_name,
            "created": d.created,
            "createdby": d.createdby.emp_name if d.createdby else None,
            "updated": d.updated,
            "updatedby": d.updatedby.emp_name if d.updatedby else None
        }
        for d in domains
    ]
    return JsonResponse(data, safe=False)


# Create a new email domain
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def create_email_domain(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        user_payload = request.user
        emp_id = user_payload.get("emp_id")
        role = user_payload.get("role")

        employee = get_object_or_404(Employee, emp_id=emp_id)
    

        data = json.loads(request.body.decode("utf-8"))
        domain_name = data.get("domain_name")
        if not domain_name:
            return JsonResponse({"error": "Missing domain_name"}, status=400)

        email_domain = EmailDomain.objects.create(
            domain_name=domain_name,
            createdby=employee,
            updatedby=employee
        )

        return JsonResponse({
            "message": "Email domain created successfully",
            "emaildomain_id": email_domain.emaildomain_id,
            "domain_name": email_domain.domain_name,
            "createdby": employee.emp_name
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Update email domain
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin",'MDGT'])
def update_email_domain(request, pk):
    if request.method != "PUT":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    user_payload = request.user
    emp_id = user_payload.get("emp_id")
    employee = get_object_or_404(Employee, emp_id=emp_id)

    

    try:
        domain = get_object_or_404(EmailDomain, pk=pk, is_deleted=False)
        data = json.loads(request.body.decode("utf-8"))
        domain.domain_name = data.get("domain_name", domain.domain_name)
        domain.updated = timezone.now()
        domain.updatedby = employee
        domain.save()

        return JsonResponse({
            "message": "Email domain updated successfully",
            "emaildomain_id": domain.emaildomain_id,
            "domain_name": domain.domain_name,
            "updatedby": employee.emp_name
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Delete email domain (soft delete)
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin"])
def delete_email_domain(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    user_payload = request.user
    emp_id = user_payload.get("emp_id")
    employee = get_object_or_404(Employee, emp_id=emp_id)

    

    try:
        domain = get_object_or_404(EmailDomain, pk=pk, is_deleted=False)
        domain.is_deleted = True
        domain.updated = timezone.now()
        domain.updatedby = employee
        domain.save()

        return JsonResponse({"message": "Email domain deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
