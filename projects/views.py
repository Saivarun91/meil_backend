from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from Common.Middleware import authenticate,restrict  # your middleware

from .models import Project
from Employee.models import Employee   # assuming Employee has emp_id & role


def is_admin_or_superadmin(user_payload):
    """Check if the logged-in user is Admin or SuperAdmin"""
    return user_payload.get("role") in ["Admin", "SuperAdmin"]

@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin"])
# def list_projects(request):
#     if request.method == "GET":
#         projects = Project.objects.all()
#         data = [
#             {
#                 "project_code": p.project_code,
#                 "project_name": p.project_name,
#                 "created": p.created,
#                 "createdby": p.createdby.username if p.createdby else None,
#                 "updated": p.updated,
#                 "updatedby": p.updatedby.username if p.updatedby else None,
#             }
#             for p in projects
#         ]
#         return JsonResponse(data, safe=False)
#     return JsonResponse({"error": "Method not allowed"}, status=405)

# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def list_projects(request):
    if request.method == "GET":
        projects = Project.objects.all()
        data = [
            {
                "project_code": p.project_code,
                "project_name": p.project_name,
                "created": p.created,
                "createdby": p.createdby.emp_name if p.createdby else None,
                "updated": p.updated,
                "updatedby": p.updatedby.emp_name if p.updatedby else None,
            }
            for p in projects
        ]
        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def create_project(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        user_payload = request.user  # from middleware
        emp_id = user_payload.get("emp_id")
        role = user_payload.get("role")

        # Validate employee exists
        employee = get_object_or_404(Employee, emp_id=emp_id)

        # Ensure Admin/SuperAdmin role
        

        # Parse request body
        data = json.loads(request.body.decode("utf-8"))
        project_code = data.get("project_code")
        project_name = data.get("project_name")

        if not project_code or not project_name:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Create project
        project = Project.objects.create(
            project_code=project_code,
            project_name=project_name,
            created=timezone.now(),
            createdby=employee,
            updated=timezone.now(),
            updatedby=employee,
            is_deleted=False
        )

        return JsonResponse({
            "message": "Project created successfully",
            "project_code": project.project_code,
            "project_name": project.project_name,
            "createdby": employee.emp_name
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
# def update_project(request, pk):
#     if request.method == "PUT":
#         user_payload = request.user_payload

#         if not is_admin_or_superadmin(user_payload):
#             return JsonResponse({"error": "Permission denied"}, status=403)

#         try:
#             project = get_object_or_404(Project, pk=pk)
#             data = json.loads(request.body)

#             emp = get_object_or_404(Employee, pk=user_payload["emp_id"])

#             project.project_name = data.get("project_name", project.project_name)
#             project.updated = timezone.now()
#             project.updatedby = emp.user
#             project.save()

#             return JsonResponse({"message": "Project updated successfully"})
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)

#     return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def update_project(request, pk):
    if request.method != "PUT":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        user_payload = request.user
        emp_id = user_payload.get("emp_id")
        role = user_payload.get("role")

        # Validate employee exists
        employee = get_object_or_404(Employee, emp_id=emp_id)

       

        project = get_object_or_404(Project, pk=pk)
        data = json.loads(request.body.decode("utf-8"))

        project.project_name = data.get("project_name", project.project_name)
        project.updated = timezone.now()
        project.updatedby = employee
        project.save()

        return JsonResponse({
            "message": "Project updated successfully",
            "project_code": project.project_code,
            "project_name": project.project_name,
            "updatedby": employee.emp_name
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin","MDGT"])
def delete_project(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        user_payload = request.user
        emp_id = user_payload.get("emp_id")
        role = user_payload.get("role")

        # Validate employee exists
        employee = get_object_or_404(Employee, emp_id=emp_id)

      

        project = get_object_or_404(Project, pk=pk)
        project.delete()  # hard delete
        return JsonResponse({"message": f"Project '{project.project_code}' deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)






