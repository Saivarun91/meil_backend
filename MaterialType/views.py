# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# import json
# from django.utils import timezone
# from .models import MaterialType
# from django.contrib.auth.models import User
# from Common.Middleware import authenticate, restrict

# @csrf_exempt
# @authenticate
# @restrict(roles=["Admin", "Manager"])
# def create_materialtype(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body.decode("utf-8"))
#             mat_type_code = data.get("mat_type_code")
#             mat_type_desc = data.get("mat_type_desc")

#             if not mat_type_code or not mat_type_desc:
#                 return JsonResponse({"error": "mat_type_code and mat_type_desc are required"}, status=400)

#             created_by_user = User.objects.filter(id=request.user.get("emp_id")).first()
#             if not created_by_user:
#                 return JsonResponse({"error": "Invalid user"}, status=400)

#             material_type = MaterialType.objects.create(
#                 mat_type_code=mat_type_code,
#                 mat_type_desc=mat_type_desc,
#                 createdby=created_by_user,
#                 updatedby=created_by_user,
#                 created=timezone.now(),
#                 updated=timezone.now()
#             )

#             response_data = {
#                 "mat_type_code": material_type.mat_type_code,
#                 "mat_type_desc": material_type.mat_type_desc,
#                 "created": material_type.created.strftime("%Y-%m-%d %H:%M:%S"),
#                 "updated": material_type.updated.strftime("%Y-%m-%d %H:%M:%S"),
#                 "createdby": created_by_user.get_full_name() or created_by_user.username,
#                 "updatedby": created_by_user.get_full_name() or created_by_user.username
#             }

#             return JsonResponse(response_data, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     return JsonResponse({"error": "Method not allowed"}, status=405)


# @csrf_exempt
# @authenticate
# @restrict(roles=["Admin", "Manager"])
# def update_materialtype(request, code):
#     if request.method == "PUT":
#         try:
#             data = json.loads(request.body.decode("utf-8"))
#             material_type = MaterialType.objects.filter(mat_type_code=code, is_deleted=False).first()

#             if not material_type:
#                 return JsonResponse({"error": "Material Type not found"}, status=404)

#             mat_type_desc = data.get("mat_type_desc")
#             if mat_type_desc:
#                 material_type.mat_type_desc = mat_type_desc

#             updated_by_user = User.objects.filter(id=request.user.get("emp_id")).first()
#             if not updated_by_user:
#                 return JsonResponse({"error": "Invalid user"}, status=400)

#             material_type.updatedby = updated_by_user
#             material_type.updated = timezone.now()
#             material_type.save()

#             response_data = {
#                 "mat_type_code": material_type.mat_type_code,
#                 "mat_type_desc": material_type.mat_type_desc,
#                 "created": material_type.created.strftime("%Y-%m-%d %H:%M:%S"),
#                 "updated": material_type.updated.strftime("%Y-%m-%d %H:%M:%S"),
#                 "createdby": material_type.createdby.get_full_name() or material_type.createdby.username if material_type.createdby else None,
#                 "updatedby": updated_by_user.get_full_name() or updated_by_user.username
#             }

#             return JsonResponse(response_data, status=200)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     return JsonResponse({"error": "Method not allowed"}, status=405)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import MaterialType
from Employee.models import Employee
from Common.Middleware import authenticate, restrict


# ✅ Utility function to get employee name from Employee object
def get_employee_name(emp):
    if emp:
        return emp.emp_name
    return None


# ✅ CREATE Material Type
@csrf_exempt
@authenticate
# @restrict(roles=["SuperAdmin", "Admin","MDGT"])
def create_material_type(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            mat_type_code = data.get("mat_type_code")
            mat_type_desc = data.get("mat_type_desc")

            if not mat_type_code or not mat_type_desc:
                return JsonResponse({"error": "mat_type_code and mat_type_desc are required"}, status=400)

            # Get Employee using emp_id from JWT
            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=400)

            material_type = MaterialType.objects.create(
                mat_type_code=mat_type_code,
                mat_type_desc=mat_type_desc,
                createdby=employee,
                updatedby=employee
            )

            response_data = {
                "mat_type_code": material_type.mat_type_code,
                "mat_type_desc": material_type.mat_type_desc,
                "created": material_type.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": material_type.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(material_type.createdby),
                "updatedby": get_employee_name(material_type.updatedby)
            }
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ✅ LIST Material Types
@csrf_exempt
@authenticate
# @restrict(roles=["SuperAdmin", "Admin","MDGT"])
def list_material_types(request):
    if request.method == "GET":
        try:
            materials = MaterialType.objects.filter(is_deleted=False)
            data = []
            for m in materials:
                data.append({
                    "mat_type_code": m.mat_type_code,
                    "mat_type_desc": m.mat_type_desc,
                    "created": m.created.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated": m.updated.strftime("%Y-%m-%d %H:%M:%S"),
                    "createdby": get_employee_name(m.createdby),
                    "updatedby": get_employee_name(m.updatedby)
                })
            return JsonResponse(data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ✅ UPDATE Material Type
@csrf_exempt
@authenticate
# @restrict(roles=["SuperAdmin", "Admin","MDGT"])
def update_material_type(request, mat_type_code):
    if request.method == "PUT":
        try:
            material_type = MaterialType.objects.filter(mat_type_code=mat_type_code, is_deleted=False).first()
            if not material_type:
                return JsonResponse({"error": "Material type not found"}, status=404)

            data = json.loads(request.body.decode("utf-8"))
            mat_type_desc = data.get("mat_type_desc")
            if mat_type_desc:
                material_type.mat_type_desc = mat_type_desc

            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=400)

            material_type.updated = timezone.now()
            material_type.updatedby = employee
            material_type.save()

            response_data = {
                "mat_type_code": material_type.mat_type_code,
                "mat_type_desc": material_type.mat_type_desc,
                "created": material_type.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": material_type.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(material_type.createdby),
                "updatedby": get_employee_name(material_type.updatedby)
            }
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ✅ DELETE Material Type (Hard Delete)
@csrf_exempt
@authenticate
# @restrict(roles=["SuperAdmin", "Admin","MDGT" ])
def delete_material_type(request, mat_type_code):
    if request.method == "DELETE":
        try:
            material_type = MaterialType.objects.filter(mat_type_code=mat_type_code).first()
            if not material_type:
                return JsonResponse({"error": "Material type not found"}, status=404)

            material_type.delete()
            return JsonResponse({"message": f"Material type {mat_type_code} deleted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
