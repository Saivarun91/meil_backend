from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from .models import MatgAttribute
from matgroups.models import MatGroup
from Employee.models import Employee
from Common.Middleware import authenticate, restrict


# ✅ Helper function
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ✅ CREATE MatgAttribute or ADD attributes to existing group
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def create_matgattribute(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        mgrp_code = data.get("mgrp_code")
        attributes_data = data.get("attributes")  # Expected dict or list of attributes

        if not mgrp_code or not isinstance(attributes_data, dict):
            return JsonResponse({"error": "Missing or invalid fields: mgrp_code, attributes"}, status=400)

        # ✅ Validate MatGroup
        matgroup = MatGroup.objects.filter(mgrp_code=mgrp_code, is_deleted=False).first()
        if not matgroup:
            return JsonResponse({"error": "MatGroup not found"}, status=404)

        emp_id = request.user.get("emp_id")
        employee = Employee.objects.filter(emp_id=emp_id).first()

        # ✅ Check if record already exists
        matg_attr = MatgAttribute.objects.filter(mgrp_code=matgroup, is_deleted=False).first()
        if matg_attr:
            # Merge with existing attributes
            matg_attr.attributes.update(attributes_data)
            matg_attr.updated = timezone.now()
            matg_attr.updatedby = employee
            matg_attr.save()
            message = "MatgAttribute updated with new attributes"
        else:
            # Create new record
            matg_attr = MatgAttribute.objects.create(
                mgrp_code=matgroup,
                attributes=attributes_data,
                createdby=employee,
                updatedby=employee
            )
            message = "MatgAttribute created successfully"

        return JsonResponse({
            "message": message,
            "attrib_id": matg_attr.attrib_id,
            "mgrp_code": matg_attr.mgrp_code.mgrp_code,
            "attributes": matg_attr.attributes,
            "created": matg_attr.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": matg_attr.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "createdby": get_employee_name(matg_attr.createdby),
            "updatedby": get_employee_name(matg_attr.updatedby)
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)


# ✅ LIST all MatgAttributes
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "User", "MDGT"])
def list_matgattributes(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    attributes = MatgAttribute.objects.filter(is_deleted=False)
    data = []
    for attr in attributes:
        data.append({
            "attrib_id": attr.attrib_id,
            "mgrp_code": attr.mgrp_code.mgrp_code if attr.mgrp_code else None,
            "attributes": attr.attributes,
            "created": attr.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": attr.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "createdby": get_employee_name(attr.createdby),
            "updatedby": get_employee_name(attr.updatedby)
        })

    return JsonResponse(data, safe=False)


# ✅ UPDATE specific MatgAttribute (merge or overwrite JSON)
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def update_matgattribute(request, attrib_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        attributes_data = data.get("attributes")
        merge = data.get("merge", True)  # Merge (default) or overwrite

        attribute = MatgAttribute.objects.filter(attrib_id=attrib_id, is_deleted=False).first()
        if not attribute:
            return JsonResponse({"error": "MatgAttribute not found"}, status=404)

        emp_id = request.user.get("emp_id")
        updatedby = Employee.objects.filter(emp_id=emp_id).first()

        # ✅ Handle update
        if not isinstance(attributes_data, dict):
            return JsonResponse({"error": "attributes must be a dictionary"}, status=400)

        if merge:
            # Merge new keys/values
            attribute.attributes.update(attributes_data)
        else:
            # Overwrite the entire JSON
            attribute.attributes = attributes_data

        attribute.updated = timezone.now()
        attribute.updatedby = updatedby
        attribute.save()

        return JsonResponse({
            "message": "MatgAttribute updated successfully",
            "attrib_id": attribute.attrib_id,
            "mgrp_code": attribute.mgrp_code.mgrp_code,
            "attributes": attribute.attributes,
            "updatedby": get_employee_name(attribute.updatedby)
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)


# ✅ DELETE an attribute key or entire record
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def delete_matgattribute(request, attrib_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    data = json.loads(request.body.decode("utf-8")) if request.body else {}
    key_to_delete = data.get("key")

    attribute = MatgAttribute.objects.filter(attrib_id=attrib_id).first()
    if not attribute:
        return JsonResponse({"error": "MatgAttribute not found"}, status=404)

    # ✅ Delete only a specific attribute key
    if key_to_delete:
        if key_to_delete in attribute.attributes:
            del attribute.attributes[key_to_delete]
            attribute.updated = timezone.now()
            attribute.save()
            return JsonResponse({"message": f"Attribute '{key_to_delete}' removed."}, status=200)
        else:
            return JsonResponse({"error": f"Key '{key_to_delete}' not found."}, status=404)

    # ✅ Or delete entire record
    attribute.delete()
    return JsonResponse({"message": "MatgAttribute deleted successfully"}, status=200)
