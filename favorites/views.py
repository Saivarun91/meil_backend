import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Favorite, SharedMaterial
from Employee.models import Employee
from matgroups.models import MatGroup
from itemmaster.models import ItemMaster
from Common.Middleware import authenticate


# Helper function
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ============================================================
# ✅ ADD Favorite (items only)
# ============================================================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def add_favorite(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        local_item_id = data.get("local_item_id")
        sap_item_id = data.get("sap_item_id")

        if not local_item_id and not sap_item_id:
            return JsonResponse({"error": "local_item_id or sap_item_id is required"}, status=400)

        # Get employee
        user = getattr(request, 'user', None)
        if not user or not isinstance(user, dict):
            return JsonResponse({"error": "User not authenticated"}, status=401)

        emp_id = user.get("emp_id")
        if not emp_id:
            return JsonResponse({"error": "Employee ID not found"}, status=400)

        employee = Employee.objects.filter(emp_id=emp_id).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # Find item by local_item_id or sap_item_id
        item = None
        if local_item_id:
            item = ItemMaster.objects.filter(
                local_item_id=local_item_id, is_deleted=False).first()
        elif sap_item_id:
            item = ItemMaster.objects.filter(
                sap_item_id=sap_item_id, is_deleted=False).first()

        if not item:
            return JsonResponse({"error": "Item not found"}, status=404)

        # Check if already favorited (not deleted)
        existing_favorite = Favorite.objects.filter(
            employee=employee,
            item=item,
            is_deleted=False
        ).first()

        if existing_favorite:
            return JsonResponse({
                "message": "Already in favorites",
                "favorite_id": existing_favorite.id
            }, status=200)

        # Check if there's a soft-deleted favorite that we can restore
        deleted_favorite = Favorite.objects.filter(
            employee=employee,
            item=item,
            is_deleted=True
        ).first()

        if deleted_favorite:
            # Restore the soft-deleted favorite
            deleted_favorite.is_deleted = False
            deleted_favorite.save()
            favorite = deleted_favorite
        else:
            # Create new favorite
            favorite = Favorite.objects.create(
                employee=employee,
                item=item
            )

        response_data = {
            "id": favorite.id,
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "item_desc": item.short_name,
            "item_long_name": item.long_name,
            "mgrp_code": item.mgrp_code.mgrp_code if item.mgrp_code else None,
            "mgrp_shortname": item.mgrp_code.mgrp_shortname if item.mgrp_code else None,
            "mgrp_longname": item.mgrp_code.mgrp_longname if item.mgrp_code else None,
            "mat_type_code": item.mat_type_code.mat_type_code if item.mat_type_code else None,
            "mat_type_desc": item.mat_type_code.mat_type_desc if item.mat_type_code else None,
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
# ✅ REMOVE Favorite (items only)
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

        local_item_id = data.get("local_item_id")
        sap_item_id = data.get("sap_item_id")

        # Get employee
        user = getattr(request, 'user', None)
        if not user or not isinstance(user, dict):
            return JsonResponse({"error": "User not authenticated"}, status=401)

        emp_id = user.get("emp_id")
        if not emp_id:
            return JsonResponse({"error": "Employee ID not found"}, status=400)

        employee = Employee.objects.filter(emp_id=emp_id).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        if favorite_id:
            # Remove by favorite ID
            favorite = Favorite.objects.filter(
                id=favorite_id,
                employee=employee,
                is_deleted=False
            ).first()
        elif local_item_id or sap_item_id:
            # Remove by item ID
            item = None
            if local_item_id:
                item = ItemMaster.objects.filter(
                    local_item_id=local_item_id).first()
            elif sap_item_id:
                item = ItemMaster.objects.filter(
                    sap_item_id=sap_item_id).first()

            if not item:
                return JsonResponse({"error": "Item not found"}, status=404)

            favorite = Favorite.objects.filter(
                employee=employee,
                item=item,
                is_deleted=False
            ).first()
        else:
            return JsonResponse({"error": "favorite_id, local_item_id, or sap_item_id is required"}, status=400)

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
# ✅ LIST Favorites (items only)
# ============================================================
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def list_favorites(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Get employee
        user = getattr(request, 'user', None)
        if not user or not isinstance(user, dict):
            return JsonResponse({"error": "User not authenticated"}, status=401)

        emp_id = user.get("emp_id")
        if not emp_id:
            return JsonResponse({"error": "Employee ID not found"}, status=400)

        employee = Employee.objects.filter(emp_id=emp_id).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # Get only item favorites
        favorites = Favorite.objects.filter(
            employee=employee,
            is_deleted=False
        ).select_related("item", "item__mgrp_code", "item__mat_type_code")

        response_data = []
        for favorite in favorites:
            if favorite.item:
                response_data.append({
                    "id": favorite.id,
                    "local_item_id": favorite.item.local_item_id,
                    "sap_item_id": favorite.item.sap_item_id,
                    "item_desc": favorite.item.short_name,
                    "item_long_name": favorite.item.long_name,
                    "mgrp_code": favorite.item.mgrp_code.mgrp_code if favorite.item.mgrp_code else None,
                    "mgrp_shortname": favorite.item.mgrp_code.mgrp_shortname if favorite.item.mgrp_code else None,
                    "mgrp_longname": favorite.item.mgrp_code.mgrp_longname if favorite.item.mgrp_code else None,
                    "mat_type_code": favorite.item.mat_type_code.mat_type_code if favorite.item.mat_type_code else None,
                    "mat_type_desc": favorite.item.mat_type_code.mat_type_desc if favorite.item.mat_type_code else None,
                    "created": favorite.created.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated": favorite.updated.strftime("%Y-%m-%d %H:%M:%S")
                })

        return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================
# ✅ SHARE Material
# ============================================================
@csrf_exempt
@authenticate
def share_material(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        local_item_id = data.get("local_item_id")
        sap_item_id = data.get("sap_item_id")
        shared_with_emp_ids = data.get(
            "shared_with", [])  # List of employee IDs

        if not local_item_id and not sap_item_id:
            return JsonResponse({"error": "local_item_id or sap_item_id is required"}, status=400)

        if not shared_with_emp_ids or not isinstance(shared_with_emp_ids, list):
            return JsonResponse({"error": "shared_with must be a list of employee IDs"}, status=400)

        # Get employee (sharer)
        user = getattr(request, 'user', None)
        if not user or not isinstance(user, dict):
            return JsonResponse({"error": "User not authenticated"}, status=401)

        emp_id = user.get("emp_id")
        if not emp_id:
            return JsonResponse({"error": "Employee ID not found"}, status=400)

        shared_by = Employee.objects.filter(emp_id=emp_id).first()
        if not shared_by:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # Find item
        item = None
        if local_item_id:
            item = ItemMaster.objects.filter(
                local_item_id=local_item_id, is_deleted=False).first()
        elif sap_item_id:
            item = ItemMaster.objects.filter(
                sap_item_id=sap_item_id, is_deleted=False).first()

        if not item:
            return JsonResponse({"error": "Item not found"}, status=404)

        # Share with multiple users
        shared_materials = []
        errors = []

        for shared_with_emp_id in shared_with_emp_ids:
            # Don't allow sharing with yourself
            if shared_with_emp_id == emp_id:
                errors.append(f"Cannot share with yourself")
                continue

            shared_with = Employee.objects.filter(
                emp_id=shared_with_emp_id, is_deleted=False).first()
            if not shared_with:
                errors.append(
                    f"Employee with ID {shared_with_emp_id} not found")
                continue

            # Check if already shared
            existing_share = SharedMaterial.objects.filter(
                shared_by=shared_by,
                shared_with=shared_with,
                item=item,
                is_deleted=False
            ).first()

            if existing_share:
                shared_materials.append({
                    "id": existing_share.id,
                    "shared_with_emp_id": shared_with.emp_id,
                    "shared_with_name": shared_with.emp_name,
                    "status": "already_shared"
                })
                continue

            # Check if soft-deleted, restore it
            deleted_share = SharedMaterial.objects.filter(
                shared_by=shared_by,
                shared_with=shared_with,
                item=item,
                is_deleted=True
            ).first()

            if deleted_share:
                deleted_share.is_deleted = False
                deleted_share.save()
                shared_materials.append({
                    "id": deleted_share.id,
                    "shared_with_emp_id": shared_with.emp_id,
                    "shared_with_name": shared_with.emp_name,
                    "status": "restored"
                })
            else:
                # Create new share
                shared_material = SharedMaterial.objects.create(
                    shared_by=shared_by,
                    shared_with=shared_with,
                    item=item
                )
                shared_materials.append({
                    "id": shared_material.id,
                    "shared_with_emp_id": shared_with.emp_id,
                    "shared_with_name": shared_with.emp_name,
                    "status": "shared"
                })

        response_data = {
            "message": f"Material shared with {len(shared_materials)} user(s)",
            "shared_materials": shared_materials,
            "item": {
                "local_item_id": item.local_item_id,
                "sap_item_id": item.sap_item_id,
                "item_desc": item.short_name
            }
        }

        if errors:
            response_data["errors"] = errors

        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================
# ✅ LIST Shared Materials (materials shared with me)
# ============================================================
@authenticate
def list_shared_materials(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Get employee
        user = getattr(request, 'user', None)
        if not user or not isinstance(user, dict):
            return JsonResponse({"error": "User not authenticated"}, status=401)

        emp_id = user.get("emp_id")
        if not emp_id:
            return JsonResponse({"error": "Employee ID not found"}, status=400)

        employee = Employee.objects.filter(emp_id=emp_id).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # Get materials shared with this employee
        shared_materials = SharedMaterial.objects.filter(
            shared_with=employee,
            is_deleted=False
        ).select_related("shared_by", "item", "item__mgrp_code", "item__mat_type_code")

        response_data = []
        for shared in shared_materials:
            if shared.item:
                response_data.append({
                    "id": shared.id,
                    "shared_by_emp_id": shared.shared_by.emp_id,
                    "shared_by_name": shared.shared_by.emp_name,
                    "shared_by_email": shared.shared_by.email,
                    "local_item_id": shared.item.local_item_id,
                    "sap_item_id": shared.item.sap_item_id,
                    "item_desc": shared.item.short_name,
                    "item_long_name": shared.item.long_name,
                    "mgrp_code": shared.item.mgrp_code.mgrp_code if shared.item.mgrp_code else None,
                    "mgrp_shortname": shared.item.mgrp_code.mgrp_shortname if shared.item.mgrp_code else None,
                    "mgrp_longname": shared.item.mgrp_code.mgrp_longname if shared.item.mgrp_code else None,
                    "mat_type_code": shared.item.mat_type_code.mat_type_code if shared.item.mat_type_code else None,
                    "mat_type_desc": shared.item.mat_type_code.mat_type_desc if shared.item.mat_type_code else None,
                    "created": shared.created.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated": shared.updated.strftime("%Y-%m-%d %H:%M:%S")
                })

        return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)
