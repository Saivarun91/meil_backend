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

# Helper function to format attributes as key:value pairs for short_name
def format_attributes_for_short_name(attributes):
    """Format attributes dictionary as 'key: value, key: value' string"""
    if not attributes or not isinstance(attributes, dict):
        return ""
    pairs = [f"{k}: {v}" for k, v in attributes.items() if v]  # Only include non-empty values
    return ", ".join(pairs)

# Helper function to format long_name with mgrp_code, mgrp_long_name, short_name
def format_long_name(mgrp_code, mgrp_long_name, short_name):
    """Format long_name as 'mgrp_code, mgrp_long_name, short_name'"""
    parts = []
    if mgrp_code:
        parts.append(str(mgrp_code))
    if mgrp_long_name:
        parts.append(str(mgrp_long_name))
    if short_name:
        parts.append(str(short_name))
    return ", ".join(parts)


# ============================================================
# ✅ CREATE ItemMaster
# ============================================================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def create_itemmaster(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        sap_item_id = data.get("sap_item_id")
        sap_name = data.get("sap_name", "")
        mat_type_code = data.get("mat_type_code")
        mgrp_code = data.get("mgrp_code")

        # Support both old field names (item_desc, notes) and new field names (short_name, long_name)
        item_desc = data.get("item_desc") or data.get("short_name")
        notes = data.get("notes", "") or data.get("long_name", "")
        search_text = data.get("search_text", "")
        selected_attributes = data.get("attributes", {})

        # Required validation
        if not mat_type_code or not mgrp_code or not item_desc:
            return JsonResponse({"error": "Required: mat_type_code, mgrp_code, item_desc (or short_name)"}, status=400)

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
            else:
                # Extract base value (remove UOM if present)
                base_value = value
                uom = allowed_attrs[key].get("uom", "")
                if uom and isinstance(value, str):
                    # Check if value ends with UOM (handle both single and multiple UOMs)
                    uom_list = []
                    if isinstance(uom, list):
                        uom_list = uom
                    elif isinstance(uom, str):
                        # Handle comma-separated UOMs
                        uom_list = [u.strip() for u in uom.split(",")] if "," in uom else [uom]
                    
                    for u in uom_list:
                        if value.endswith(f" {u}"):
                            base_value = value.replace(f" {u}", "")
                            break
                
                # Allow custom values (values not in possible_values) - user requirement
                # Only validate that the attribute name exists, not the value
                # Custom values are allowed for flexibility
                pass  # No validation needed for custom values

        if invalid_fields:
            return JsonResponse({
                "error": "Invalid attribute selection",
                "details": invalid_fields
            }, status=400)

        # ===============================================================
        # ✅ Check for duplicate materials with same attributes and material group
        # ===============================================================
        # Skip duplicate check if force_create flag is set
        force_create = data.get("force_create", False)
        if not force_create and selected_attributes and any(selected_attributes.values()):
            # Normalize attributes for comparison (remove UOMs, trim values)
            normalized_new_attrs = {}
            for key, value in selected_attributes.items():
                if value:
                    # Remove UOM if present
                    normalized_value = str(value).strip()
                    # Check if value ends with UOM
                    uom = allowed_attrs.get(key, {}).get("uom", "")
                    if uom:
                        uom_list = []
                        if isinstance(uom, list):
                            uom_list = uom
                        elif isinstance(uom, str):
                            uom_list = [u.strip() for u in uom.split(",")] if "," in uom else [uom]
                        for u in uom_list:
                            if normalized_value.endswith(f" {u}"):
                                normalized_value = normalized_value.replace(f" {u}", "").strip()
                                break
                    normalized_new_attrs[key] = normalized_value
            
            # Find existing materials with same mgrp_code and matching attributes
            existing_items = ItemMaster.objects.filter(
                mgrp_code=mat_group,
                is_deleted=False
            )
            
            duplicate_items = []
            for existing_item in existing_items:
                if existing_item.attributes:
                    # Normalize existing attributes
                    normalized_existing_attrs = {}
                    for key, value in existing_item.attributes.items():
                        if value:
                            normalized_value = str(value).strip()
                            # Remove UOM if present
                            uom = allowed_attrs.get(key, {}).get("uom", "")
                            if uom:
                                uom_list = []
                                if isinstance(uom, list):
                                    uom_list = uom
                                elif isinstance(uom, str):
                                    uom_list = [u.strip() for u in uom.split(",")] if "," in uom else [uom]
                                for u in uom_list:
                                    if normalized_value.endswith(f" {u}"):
                                        normalized_value = normalized_value.replace(f" {u}", "").strip()
                                        break
                            normalized_existing_attrs[key] = normalized_value
                    
                    # Compare normalized attributes
                    if normalized_new_attrs == normalized_existing_attrs:
                        duplicate_items.append({
                            "local_item_id": existing_item.local_item_id,
                            "sap_item_id": existing_item.sap_item_id,
                            "mgrp_code": existing_item.mgrp_code.mgrp_code,
                            "short_name": existing_item.short_name,
                            "attributes": existing_item.attributes
                        })
            
            # If duplicates found, return warning with duplicate information
            if duplicate_items:
                return JsonResponse({
                    "warning": "Material found with same attributes and material group",
                    "duplicates": duplicate_items,
                    "message": f"Found {len(duplicate_items)} existing material(s) with the same attributes in material group {mgrp_code}"
                }, status=200)  # Use 200 instead of error to allow frontend to handle it
        
        # Get mgrp_long_name from MatGroup
        mgrp_long_name = mat_group.mgrp_longname if mat_group else None
        
        # Format short_name: if attributes are provided, use formatted attributes, otherwise use item_desc
        if selected_attributes and any(selected_attributes.values()):
            formatted_short_name = format_attributes_for_short_name(selected_attributes)
            # If formatted attributes is empty or too short, fall back to item_desc
            if not formatted_short_name or len(formatted_short_name) < 3:
                formatted_short_name = item_desc
        else:
            formatted_short_name = item_desc
        
        # Format long_name with mgrp_code, mgrp_long_name, short_name
        formatted_long_name = format_long_name(
            mat_group.mgrp_code if mat_group else None,
            mgrp_long_name,
            formatted_short_name
        )

        # Create ItemMaster
        item = ItemMaster.objects.create(
            sap_item_id=sap_item_id,
            sap_name=sap_name,
            mat_type_code=material_type,
            mgrp_code=mat_group,
            short_name=formatted_short_name,
            long_name=formatted_long_name,
            mgrp_long_name=mgrp_long_name,  # Store mgrp_long_name separately
            search_text=search_text,
            attributes=selected_attributes,
            createdby=employee,
            updatedby=employee
        )

        response_data = {
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "sap_name": item.sap_name,
            "mat_type_code": item.mat_type_code.mat_type_code,
            "mgrp_code": item.mgrp_code.mgrp_code,
            "item_desc": item.short_name,  # Map to old field name for frontend compatibility
            "short_name": item.short_name,
            "attributes": item.attributes,
            "notes": item.long_name,  # Map to old field name for frontend compatibility
            "long_name": item.long_name,
            "search_text": item.search_text,
            "is_final": item.is_final,
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
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def list_itemmasters(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    items = ItemMaster.objects.filter(is_deleted=False)
    response_data = []

    for item in items:
        response_data.append({
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "sap_name": item.sap_name,
            "mat_type_code": item.mat_type_code.mat_type_code,
            "mgrp_code": item.mgrp_code.mgrp_code,
            "mgrp_long_name": item.mgrp_long_name,
            "item_desc": item.short_name,  # Map to old field name for frontend compatibility
            "short_name": item.short_name,
            "attributes": item.attributes,
            "notes": item.long_name,  # Map to old field name for frontend compatibility
            "long_name": item.long_name,
            "search_text": item.search_text,
            "is_final": item.is_final,
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
# @restrict(roles=["Admin", "SuperAdmin", "MDGT"])
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
            # Update mgrp_long_name from MatGroup
            item.mgrp_long_name = mat_group.mgrp_longname if mat_group else None

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
                else:
                    # Extract base value (remove UOM if present)
                    base_value = value
                    uom = allowed_attrs[key].get("uom", "")
                    if uom and isinstance(value, str):
                        # Check if value ends with UOM (handle both single and multiple UOMs)
                        uom_list = []
                        if isinstance(uom, list):
                            uom_list = uom
                        elif isinstance(uom, str):
                            # Handle comma-separated UOMs
                            uom_list = [u.strip() for u in uom.split(",")] if "," in uom else [uom]
                        
                        for u in uom_list:
                            if value.endswith(f" {u}"):
                                base_value = value.replace(f" {u}", "")
                                break
                    
                    # Allow custom values (values not in possible_values) - user requirement
                    # Only validate that the attribute name exists, not the value
                    # Custom values are allowed for flexibility
                    pass  # No validation needed for custom values

            if invalid_fields:
                return JsonResponse({
                    "error": "Invalid attribute selection",
                    "details": invalid_fields
                }, status=400)

            item.attributes = selected_attributes
            # Auto-update short_name with formatted attributes if attributes are provided
            if selected_attributes and any(selected_attributes.values()):
                formatted_short_name = format_attributes_for_short_name(selected_attributes)
                if formatted_short_name and len(formatted_short_name) >= 3:
                    item.short_name = formatted_short_name

        # Standard updates
        item.sap_item_id = data.get("sap_item_id", item.sap_item_id)
        item.sap_name = data.get("sap_name", item.sap_name)
        
        # Support both old and new field names for item_desc/short_name
        # But only if attributes weren't already used to update short_name
        if "attributes" not in data and ("item_desc" in data or "short_name" in data):
            item.short_name = data.get("item_desc") or data.get("short_name") or item.short_name
        
        item.search_text = data.get("search_text", item.search_text)
        
        # Update is_final if provided
        if "is_final" in data:
            item.is_final = data.get("is_final", False)

        # Always update long_name with mgrp_code, mgrp_long_name, short_name
        item.long_name = format_long_name(
            item.mgrp_code.mgrp_code if item.mgrp_code else None,
            item.mgrp_long_name,
            item.short_name
        )

        # Audit
        item.updated = timezone.now()
        item.updatedby = Employee.objects.filter(emp_id=request.user.get("emp_id")).first()
        item.save()

        response_data = {
            "local_item_id": item.local_item_id,
            "sap_item_id": item.sap_item_id,
            "sap_name": item.sap_name,
            "mat_type_code": item.mat_type_code.mat_type_code,
            "mgrp_code": item.mgrp_code.mgrp_code,
            "item_desc": item.short_name,  # Map to old field name for frontend compatibility
            "short_name": item.short_name,
            "attributes": item.attributes,
            "notes": item.long_name,  # Map to old field name for frontend compatibility
            "long_name": item.long_name,
            "search_text": item.search_text,
            "is_final": item.is_final,
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
# @restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def delete_itemmaster(request, local_item_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    item = ItemMaster.objects.filter(local_item_id=local_item_id).first()
    if not item:
        return JsonResponse({"error": "ItemMaster not found"}, status=404)

    item.is_deleted = True
    item.save()

    return JsonResponse({"message": "ItemMaster deleted successfully"}, status=200)
