import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ItemMaster
from Employee.models import Employee
from MaterialType.models import MaterialType
from matgroups.models import MatGroup
from matg_attributes.models import MatgAttribute  # ✅ Import this to fetch allowed attributes
from Common.Middleware import authenticate, restrict


# ✅ Helper function to get employee name
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ======================================
# CREATE ItemMaster
# ======================================
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def create_itemmaster(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        print("🧠 Incoming Data:", data)  # ✅ Add this
        sap_item_id = data.get("sap_item_id")
        mat_type_code = data.get("mat_type_code")
        mgrp_code = data.get("mgrp_code")
        
        item_desc = data.get("item_desc")
        notes = data.get("notes", "")
        search_text = data.get("search_text", "")
        selected_attributes = data.get("attributes", {})  # ✅ User selected attribute values

        # Validate required fields
        if not mat_type_code or not mgrp_code or not item_desc:
            return JsonResponse({"error": "Required fields: mat_type_code, mgrp_code, item_desc"}, status=400)

        # ✅ Validate Employee
        emp_id = request.user.get("emp_id")
        employee = Employee.objects.filter(emp_id=emp_id).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=400)

        # ✅ Validate MaterialType
        material_type = MaterialType.objects.filter(mat_type_code=mat_type_code).first()
        if not material_type:
            return JsonResponse({"error": f"MaterialType with code {mat_type_code} not found"}, status=400)

        # ✅ Validate MatGroup
        mat_group = MatGroup.objects.filter(mgrp_code=mgrp_code).first()
        if not mat_group:
            return JsonResponse({"error": f"MatGroup with code {mgrp_code} not found"}, status=400)

        # ✅ Fetch allowed attributes for that group
        matg_attr = MatgAttribute.objects.filter(mgrp_code=mat_group, is_deleted=False).first()
        allowed_attrs = matg_attr.attributes if matg_attr else {}

        # ✅ Validate user-selected attributes
        invalid_fields = []
        for key, value in selected_attributes.items():
            if key not in allowed_attrs:
                invalid_fields.append(f"{key} not defined in MatGroup {mgrp_code}")
            elif value not in allowed_attrs[key].get("values", []):
                invalid_fields.append(f"{value} not valid for {key} in MatGroup {mgrp_code}")

        if invalid_fields:
            return JsonResponse({"error": "Invalid attribute selection", "details": invalid_fields}, status=400)

        # ✅ Create ItemMaster
        item = ItemMaster.objects.create(
            sap_item_id=sap_item_id,
            mat_type_code=material_type,
            mgrp_code=mat_group,
            item_desc=item_desc,
            notes=notes,
            search_text=search_text,
            attributes=selected_attributes,  # ✅ Save selected attributes
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
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print("error", e)
        return JsonResponse({"error": str(e)}, status=500)


# ======================================
# LIST ItemMasters
# ======================================
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
            "attributes": item.attributes,  # ✅ Include selected attributes
            "notes": item.notes,
            "search_text": item.search_text,
            "created": item.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": item.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "createdby": get_employee_name(item.createdby),
            "updatedby": get_employee_name(item.updatedby)
        })
    return JsonResponse(response_data, safe=False, status=200)


# ======================================
# UPDATE ItemMaster
# ======================================
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

        # ✅ Handle related fields
        if "mat_type_code" in data:
            mat_type_code = data.get("mat_type_code")
            material_type = MaterialType.objects.filter(mat_type_code=mat_type_code).first()
            if not material_type:
                return JsonResponse({"error": f"MaterialType {mat_type_code} not found"}, status=400)
            item.mat_type_code = material_type

        if "mgrp_code" in data:
            mgrp_code = data.get("mgrp_code")
            mat_group = MatGroup.objects.filter(mgrp_code=mgrp_code).first()
            if not mat_group:
                return JsonResponse({"error": f"MatGroup {mgrp_code} not found"}, status=400)
            item.mgrp_code = mat_group

        # ✅ Validate and update attributes
        if "attributes" in data:
            selected_attributes = data["attributes"]
            matg_attr = MatgAttribute.objects.filter(mgrp_code=item.mgrp_code, is_deleted=False).first()
            allowed_attrs = matg_attr.attributes if matg_attr else {}

            invalid_fields = []
            for key, value in selected_attributes.items():
                if key not in allowed_attrs:
                    invalid_fields.append(f"{key} not defined in MatGroup {item.mgrp_code.mgrp_code}")
                elif value not in allowed_attrs[key].get("values", []):
                    invalid_fields.append(f"{value} not valid for {key}")

            if invalid_fields:
                return JsonResponse({"error": "Invalid attribute selection", "details": invalid_fields}, status=400)

            item.attributes = selected_attributes  # ✅ Update attributes safely

        # ✅ Other fields
        item.sap_item_id = data.get("sap_item_id", item.sap_item_id)
        item.item_desc = data.get("item_desc", item.item_desc)
        item.notes = data.get("notes", item.notes)
        item.search_text = data.get("search_text", item.search_text)

        # ✅ Audit fields
        emp_id = request.user.get("emp_id")
        employee = Employee.objects.filter(emp_id=emp_id).first()
        item.updatedby = employee
        item.updated = timezone.now()
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
            "created": item.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": item.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "createdby": get_employee_name(item.createdby),
            "updatedby": get_employee_name(item.updatedby)
        }
        return JsonResponse(response_data, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print("error", e)
        return JsonResponse({"error": str(e)}, status=500)


# ======================================
# DELETE ItemMaster
# ======================================
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def delete_itemmaster(request, local_item_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    item = ItemMaster.objects.filter(local_item_id=local_item_id).first()
    if not item:
        return JsonResponse({"error": "ItemMaster not found"}, status=404)

    item.delete()
    return JsonResponse({"message": "ItemMaster deleted successfully"}, status=200)
