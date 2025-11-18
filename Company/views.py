from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
import json
from .models import Company
from Employee.models import Employee  # adjust path if needed
from Common.Middleware import authenticate, restrict
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin"])  # only admins can create companies
def create_company(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            company_name = data.get("company_name")
            contact = data.get("contact")
            if not company_name:
                return JsonResponse({"message": "Company name is required"}, status=400)
            if Company.objects.filter(company_name=company_name, is_deleted=False).exists():
                return JsonResponse({"message": "Company already exists"}, status=400)
            company = Company.objects.create(
                company_name=company_name,
                contact=contact,
                # createdby_id=request.user.get("emp_id"),
                # updatedby_id=request.user.get("emp_id")
            )
            return JsonResponse({
                "message": "Company created successfully",
                "company": company.company_name
            }, status=201)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin"])
def list_companies(request):
    if request.method == "GET":
        companies = Company.objects.filter(is_deleted=False).values(
            "company_name", "created", "updated", "contact"
        )
        return JsonResponse(list(companies), safe=False)

# Public endpoint for registration (no authentication required)
@csrf_exempt
def list_companies_public(request):
    if request.method == "GET":
        companies = Company.objects.filter(is_deleted=False).values(
            "company_name", "contact"
        ).order_by("company_name")
        return JsonResponse(list(companies), safe=False)

@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin"])
def update_company(request, company_name):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            new_name = data.get("company_name")
            contact = data.get("contact")
            if not new_name:
                return JsonResponse({"message": "New company name is required"}, status=400)
            # Check if old company exists
            if not Company.objects.filter(company_name=company_name, is_deleted=False).exists():
                return JsonResponse({"message": "Company not found"}, status=404)
            # Check if new name already exists
            # if Company.objects.filter(company_name=new_name, is_deleted=False).exists():
            #     return JsonResponse({"message": "Company with this name already exists"}, status=400)
            # Perform the update directly on the DB
            Company.objects.filter(company_name=company_name).update(
                company_name=new_name,
                contact=contact,
                updated=timezone.now(),
                # updatedby_id=request.user.get("emp_id")
            )
            return JsonResponse({"message": "Company updated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    return JsonResponse({"message": "Method Not Allowed"}, status=405)

@csrf_exempt
@authenticate
@restrict(roles=["Admin", " SuperAdmin"])
def delete_company(request, company_name):
    if request.method == "DELETE":
        try:
            try:
                company = Company.objects.get(company_name=company_name)
            except Company.DoesNotExist:
                return JsonResponse({"message": "Company not found"}, status=404)

            company.delete()  # Hard delete
            return JsonResponse({"message": "Company deleted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    return JsonResponse({"message": "Method Not Allowed"}, status=405)

