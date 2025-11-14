import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import ItemMaster
from Employee.models import Employee
from MaterialType.models import MaterialType
from matgroups.models import MatGroup
from matg_attributes.models import MatgAttributeItem  # NEW model
from Common.Middleware import authenticate, restrict


# Helper function
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ============================================================
# ✅ CREATE ItemMaster
# ============================================================
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def create_itemmaster(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        sap_item_id = data.get("sap_item_id")
        mat_type_code = data.get("mat_type_code")
        mgrp_code = data.get("mgrp_code")

        item_desc = data.get("item_desc")
        notes = data.get("notes", "")
        search_text = data.get("search_text", "")
        selected_attributes = data.get("attributes", {})

        # Required validation
        if not mat_type_code or not mgrp_code or not item_desc:
            return JsonResponse({"error": "Required: mat_type_code, mgrp_code, item_desc"}, status=400)

        # Validate Employee
        employee = Employee.objects.filter(emp_id=request.user.get("emp_id")).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # Validate MaterialType
        material_type = MaterialType.objects.filter(mat_type_code=mat_type_code).first()
        if not material_type:
            return JsonResponse({"error": f"MaterialType {mat_type_code} not found"}, status=400)

        # Validate MatGroup
        mat_group = MatGroup.objects.filter(mgrp_code=mgrp_code).first()
        if not mat_group:
            return JsonResponse({"error": f"MatGroup {mgrp_code} not found"}, status=400)

        # ===============================================================
        # ✅ Fetch allowed attributes from new MatgAttributeItem model
        # ===============================================================
        attr_items = MatgAttributeItem.objects.filter(
            mgrp_code=mat_group,
            is_deleted=False
        )

        allowed_attrs = {
            item.attribute_name: {
                "values": item.possible_values,
                "uom": item.uom,
            }
            for item in attr_items
        }
        # ===============================================================

        # Validate user-selected attributes
        invalid_fields = []

        for key, value in selected_attributes.items():
            if key not in allowed_attrs:
                invalid_fields.append(f"'{key}' is not defined for MatGroup {mgrp_code}")
            elif value not in allowed_attrs[key]["values"]:
                invalid_fields.append(f"'{value}' is not valid for '{key}'")

        if invalid_fields:
            return JsonResponse({
                "error": "Invalid attribute selection",
                "details": invalid_fields
            }, status=400)

        # Create ItemMaster
        item = ItemMaster.objects.create(
            sap_item_id=sap_item_id,
            mat_type_code=material_type,
            mgrp_code=mat_group,
            item_desc=item_desc,
            notes=notes,
            search_text=search_text,
            attributes=selected_attributes,
            createdby=employee,
            updatedby=employee
        )

        response_data = {
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "mat_type_code": item.mat_type_code.mat_type_code,
            "mgrp_code": item.mgrp_code.mgrp_code,
            "item_desc": item.item_desc,
            "attributes": item.attributes,
            "notes": item.notes,
            "search_text": item.search_text,
            "created": item.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": item.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "createdby": get_employee_name(item.createdby),
            "updatedby": get_employee_name(item.updatedby)
        }

        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)



# ============================================================
# ✅ LIST ItemMasters
# ============================================================
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def list_itemmasters(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    items = ItemMaster.objects.filter(is_deleted=False)
    response_data = []

    for item in items:
        response_data.append({
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "mat_type_code": item.mat_type_code.mat_type_code,
            "mgrp_code": item.mgrp_code.mgrp_code,
            "item_desc": item.item_desc,
            "attributes": item.attributes,
            "notes": item.notes,
            "search_text": item.search_text,
            "created": item.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": item.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "createdby": get_employee_name(item.createdby),
            "updatedby": get_employee_name(item.updatedby)
        })

    return JsonResponse(response_data, safe=False, status=200)



# ============================================================
# ✅ UPDATE ItemMaster
# ============================================================
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def update_itemmaster(request, local_item_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        item = ItemMaster.objects.filter(local_item_id=local_item_id, is_deleted=False).first()
        if not item:
            return JsonResponse({"error": "ItemMaster not found"}, status=404)

        # Update MaterialType
        if "mat_type_code" in data:
            mat_type = MaterialType.objects.filter(mat_type_code=data["mat_type_code"]).first()
            if not mat_type:
                return JsonResponse({"error": f"MaterialType {data['mat_type_code']} not found"}, status=400)
            item.mat_type_code = mat_type

        # Update MatGroup
        if "mgrp_code" in data:
            mat_group = MatGroup.objects.filter(mgrp_code=data["mgrp_code"]).first()
            if not mat_group:
                return JsonResponse({"error": f"MatGroup {data['mgrp_code']} not found"}, status=400)
            item.mgrp_code = mat_group

        # ===============================================================
        # Validate attributes if provided
        # ===============================================================
        if "attributes" in data:
            selected_attributes = data["attributes"]

            attr_items = MatgAttributeItem.objects.filter(
                mgrp_code=item.mgrp_code,
                is_deleted=False
            )

            allowed_attrs = {
                a.attribute_name: {"values": a.possible_values, "uom": a.uom}
                for a in attr_items
            }

            invalid_fields = []

            for key, value in selected_attributes.items():
                if key not in allowed_attrs:
                    invalid_fields.append(f"{key} not defined")
                elif value not in allowed_attrs[key]["values"]:
                    invalid_fields.append(f"{value} invalid for {key}")

            if invalid_fields:
                return JsonResponse({
                    "error": "Invalid attribute selection",
                    "details": invalid_fields
                }, status=400)

            item.attributes = selected_attributes

        # Standard updates
        item.sap_item_id = data.get("sap_item_id", item.sap_item_id)
        item.item_desc = data.get("item_desc", item.item_desc)
        item.notes = data.get("notes", item.notes)
        item.search_text = data.get("search_text", item.search_text)

        # Audit
        item.updated = timezone.now()
        item.updatedby = Employee.objects.filter(emp_id=request.user.get("emp_id")).first()
        item.save()

        response_data = {
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "mat_type_code": item.mat_type_code.mat_type_code,
            "mgrp_code": item.mgrp_code.mgrp_code,
            "item_desc": item.item_desc,
            "attributes": item.attributes,
            "notes": item.notes,
            "search_text": item.search_text,
            "updated": item.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "updatedby": get_employee_name(item.updatedby)
        }

        return JsonResponse(response_data, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)



# ============================================================
# ✅ DELETE ItemMaster
# ============================================================
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def delete_itemmaster(request, local_item_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    item = ItemMaster.objects.filter(local_item_id=local_item_id).first()
    if not item:
        return JsonResponse({"error": "ItemMaster not found"}, status=404)

    item.is_deleted = True
    item.save()

    return JsonResponse({"message": "ItemMaster deleted successfully"}, status=200)
