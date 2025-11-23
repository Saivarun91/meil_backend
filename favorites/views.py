import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Favorite
from Employee.models import Employee
from matgroups.models import MatGroup
from Common.Middleware import authenticate


# Helper function
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ============================================================
# ✅ ADD Favorite
# ============================================================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def add_favorite(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        mgrp_code = data.get("mgrp_code")

        if not mgrp_code:
            return JsonResponse({"error": "mgrp_code is required"}, status=400)

        # Get employee
        employee = Employee.objects.filter(emp_id=request.user.get("emp_id")).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # Validate material group
        mat_group = MatGroup.objects.filter(mgrp_code=mgrp_code, is_deleted=False).first()
        if not mat_group:
            return JsonResponse({"error": f"Material Group {mgrp_code} not found"}, status=404)

        # Check if already favorited
        existing_favorite = Favorite.objects.filter(
            employee=employee,
            mgrp_code=mat_group,
            is_deleted=False
        ).first()

        if existing_favorite:
            return JsonResponse({
                "message": "Already in favorites",
                "favorite_id": existing_favorite.id
            }, status=200)

        # Create favorite
        favorite = Favorite.objects.create(
            employee=employee,
            mgrp_code=mat_group
        )

        response_data = {
            "id": favorite.id,
            "mgrp_code": favorite.mgrp_code.mgrp_code,
            "mgrp_shortname": favorite.mgrp_code.mgrp_shortname,
            "mgrp_longname": favorite.mgrp_code.mgrp_longname,
            "created": favorite.created.strftime("%Y-%m-%d %H:%M:%S"),
            "employee": get_employee_name(employee)
        }

        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================
# ✅ REMOVE Favorite
# ============================================================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def remove_favorite(request, favorite_id=None):
    if request.method != "DELETE" and request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = {}
        if request.body:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except:
                pass
        mgrp_code = data.get("mgrp_code") or (request.GET.get("mgrp_code") if request.method == "DELETE" else None)

        # Get employee
        employee = Employee.objects.filter(emp_id=request.user.get("emp_id")).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        if favorite_id:
            # Remove by favorite ID
            favorite = Favorite.objects.filter(
                id=favorite_id,
                employee=employee,
                is_deleted=False
            ).first()
        elif mgrp_code:
            # Remove by mgrp_code
            mat_group = MatGroup.objects.filter(mgrp_code=mgrp_code).first()
            if not mat_group:
                return JsonResponse({"error": f"Material Group {mgrp_code} not found"}, status=404)

            favorite = Favorite.objects.filter(
                employee=employee,
                mgrp_code=mat_group,
                is_deleted=False
            ).first()
        else:
            return JsonResponse({"error": "favorite_id or mgrp_code is required"}, status=400)

        if not favorite:
            return JsonResponse({"error": "Favorite not found"}, status=404)

        favorite.is_deleted = True
        favorite.save()

        return JsonResponse({"message": "Favorite removed successfully"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================
# ✅ LIST Favorites
# ============================================================
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def list_favorites(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Get employee
        employee = Employee.objects.filter(emp_id=request.user.get("emp_id")).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        favorites = Favorite.objects.filter(
            employee=employee,
            is_deleted=False
        ).select_related("mgrp_code")

        response_data = []
        for favorite in favorites:
            response_data.append({
                "id": favorite.id,
                "mgrp_code": favorite.mgrp_code.mgrp_code,
                "mgrp_shortname": favorite.mgrp_code.mgrp_shortname,
                "mgrp_longname": favorite.mgrp_code.mgrp_longname,
                "created": favorite.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": favorite.updated.strftime("%Y-%m-%d %H:%M:%S")
            })

        return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

