from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .decorators import role_required  # import your decorator

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@role_required(["SUPERADMIN"])  # Only SUPERADMIN users can access
def employee_crud(request, emp_id=None):
    """
    Single endpoint for Employee CRUD.
    GET    -> list all or get detail
    POST   -> create
    PUT    -> update
    DELETE -> soft delete
    """
    # You no longer need an internal SUPERADMIN check
    if request.method == "GET":
        if emp_id:
            emp = get_object_or_404(Employee, emp_id=emp_id, is_deleted=False)
            return JsonResponse({
                "emp_id": emp.emp_id,
                "emp_name": emp.emp_name,
                "company_name": emp.company_name.name
            })
        else:
            employees = Employee.objects.filter(is_deleted=False).values(
                "emp_id", "emp_name", "company_name__name"
            )
            return JsonResponse(list(employees), safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)
        emp = Employee.objects.create(
            emp_name=data.get("emp_name"),
            company_name_id=data.get("company_id"),
            createdby=request.user,
            updatedby=request.user
        )
        return JsonResponse({"emp_id": emp.emp_id, "message": "Employee created"}, status=201)

    elif request.method == "PUT":
        if not emp_id:
            return HttpResponseBadRequest("Employee ID required for update")
        emp = get_object_or_404(Employee, emp_id=emp_id, is_deleted=False)
        data = json.loads(request.body)
        emp.emp_name = data.get("emp_name", emp.emp_name)
        if "company_id" in data:
            emp.company_name_id = data["company_id"]
        emp.updatedby = request.user
        emp.save()
        return JsonResponse({"message": "Employee updated"})

    elif request.method == "DELETE":
        if not emp_id:
            return HttpResponseBadRequest("Employee ID required for delete")
        emp = get_object_or_404(Employee, emp_id=emp_id, is_deleted=False)
        emp.is_deleted = True
        emp.updatedby = request.user
        emp.save()
        return JsonResponse({"message": "Employee deleted"})

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
