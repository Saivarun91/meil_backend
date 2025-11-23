from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Permission
from Users.models import UserRole
from Common.Middleware import authenticate, restrict
from Employee.models import Employee


def get_role_names(permission):
    return [role.role_name for role in permission.roles.all()]


@csrf_exempt
@authenticate
# @restrict(roles=["Admin"])
def list_permissions(request):
    if request.method == "GET":
        permissions = Permission.objects.all()
        data = []

        for perm in permissions:
            roles_data = {}
            for role in perm.roles.all():  # related_name="roles"
                roles_data[role.role_name] = {
                    "create": role.can_create,
                    "write": role.can_update,
                    "delete": role.can_delete,
                    "export": role.can_export
                }

            data.append({
                "permission_id": perm.permission_id,
                "permission_name": perm.permission_name,
                "permission_description": perm.permission_description,
                "roles": [r.role_name for r in perm.roles.all()],
                "access": roles_data,
                "template_roles": perm.template_role or {}  # ✅ you added this
            })

        return JsonResponse(data, safe=False, status=200)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin"])
def create_permission_for_role(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            perm_name = data.get("permission_name")
            template_roles = data.get("template_roles")

            if not perm_name or not template_roles or not isinstance(template_roles, dict):
                return JsonResponse(
                    {"error": "permission_name and template_roles (dict) are required"},
                    status=400
                )

            # ✅ Get Employee instance using emp_id from middleware
            try:
                employee_instance = Employee.objects.get(
                    pk=request.user["emp_id"])
            except Employee.DoesNotExist:
                return JsonResponse({"error": "Employee not found"}, status=404)

            # ✅ Create or update Permission
            permission, created = Permission.objects.get_or_create(
                permission_name=perm_name,
                defaults={
                    "permission_description": data.get("permission_description", ""),
                    "createdby": employee_instance,
                }
            )

            # ✅ Merge roles
            existing_roles = permission.template_role or {}
            existing_roles.update(template_roles)
            permission.template_role = existing_roles
            permission.updatedby = employee_instance
            permission.save()

            return JsonResponse({
                "message": "Permission created/updated with template roles",
                "permission": {
                    "id": permission.permission_id,
                    "name": permission.permission_name,
                    "template_roles": permission.template_role
                }
            }, status=201 if created else 200)

        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Method not allowed"}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin"])
def permission_detail(request, pk):
    try:
        permission = Permission.objects.get(pk=pk)
    except Permission.DoesNotExist:
        return JsonResponse({"message": "Permission not found"}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "permission_id": permission.permission_id,
            "permission_name": permission.permission_name,
            "permission_description": permission.permission_description,
            "roles": get_role_names(permission),
        })

    elif request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Update basic fields
            permission.permission_name = data.get(
                "permission_name", permission.permission_name)
            permission.permission_description = data.get(
                "permission_description", permission.permission_description)

            # ✅ Replace template_roles completely instead of merging
            updates = data.get("template_roles")
            if updates is not None and isinstance(updates, dict):
                permission.template_role = updates  # overwrite with new dict

            # Get Employee instance
            try:
                employee_instance = Employee.objects.get(
                    pk=request.user["emp_id"])
            except Employee.DoesNotExist:
                return JsonResponse({"error": "Employee not found"}, status=404)

            permission.updatedby = employee_instance
            permission.save()

            return JsonResponse({
                "message": "Permission updated successfully",
                "permission": {
                    "id": permission.permission_id,
                    "name": permission.permission_name,
                    "description": permission.permission_description,
                    "template_roles": permission.template_role
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "DELETE":
        permission.delete()
        return JsonResponse({"message": "Permission deleted"}, status=204)

    return JsonResponse({"message": "Method not allowed"}, status=405)