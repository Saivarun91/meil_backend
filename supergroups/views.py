from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json
from .models import SuperGroup
from Employee.models import Employee
from Common.Middleware import authenticate, restrict


# ✅ Helper to get employee name
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ✅ CREATE SuperGroup
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def create_supergroup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            sgrp_code = data.get("sgrp_code")
            sgrp_name = data.get("sgrp_name")
            dept_name = data.get("dept_name")

            if not sgrp_code or not sgrp_name or not dept_name:
                return JsonResponse({"error": "All fields (sgrp_code, sgrp_name, dept_name) are required"}, status=400)

            # ✅ Get Employee for createdby
            emp_id = request.user.get("emp_id")
            createdby = Employee.objects.filter(emp_id=emp_id).first()

            supergroup = SuperGroup.objects.create(
                sgrp_code=sgrp_code,
                sgrp_name=sgrp_name,
                dept_name=dept_name,
                createdby=createdby,
                updatedby=createdby
            )

            response_data = {
                "sgrp_code": supergroup.sgrp_code,
                "sgrp_name": supergroup.sgrp_name,
                "dept_name": supergroup.dept_name,
                "created": supergroup.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": supergroup.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(supergroup.createdby),
                "updatedby": get_employee_name(supergroup.updatedby)
            }
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ✅ LIST all SuperGroups (excluding deleted)
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "User","MDGT"])
def list_supergroups(request):
    if request.method == "GET":
        supergroups = SuperGroup.objects.filter(is_deleted=False)
        response_data = []
        for sg in supergroups:
            response_data.append({
                "sgrp_code": sg.sgrp_code,
                "sgrp_name": sg.sgrp_name,
                "dept_name": sg.dept_name,
                "created": sg.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": sg.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(sg.createdby),
                "updatedby": get_employee_name(sg.updatedby)
            })
        return JsonResponse(response_data, safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ✅ UPDATE SuperGroup
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def update_supergroup(request, sgrp_code):
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))

            supergroup = SuperGroup.objects.filter(sgrp_code=sgrp_code, is_deleted=False).first()
            if not supergroup:
                return JsonResponse({"error": "SuperGroup not found"}, status=404)

            supergroup.sgrp_name = data.get("sgrp_name", supergroup.sgrp_name)
            supergroup.dept_name = data.get("dept_name", supergroup.dept_name)

            # ✅ Update updatedby
            emp_id = request.user.get("emp_id")
            updatedby = Employee.objects.filter(emp_id=emp_id).first()
            supergroup.updatedby = updatedby
            supergroup.updated = timezone.now()

            supergroup.save()

            response_data = {
                "sgrp_code": supergroup.sgrp_code,
                "sgrp_name": supergroup.sgrp_name,
                "dept_name": supergroup.dept_name,
                "created": supergroup.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": supergroup.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(supergroup.createdby),
                "updatedby": get_employee_name(supergroup.updatedby)
            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ✅ HARD DELETE SuperGroup
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def delete_supergroup(request, sgrp_code):
    if request.method == "DELETE":
        supergroup = SuperGroup.objects.filter(sgrp_code=sgrp_code).first()
        if not supergroup:
            return JsonResponse({"error": "SuperGroup not found"}, status=404)

        supergroup.delete()  # ✅ Hard delete
        return JsonResponse({"message": "SuperGroup deleted successfully"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)
