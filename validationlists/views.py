from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import get_user_model
import json

from .models import ValidationLists

User = get_user_model()


# List all
def validation_list_all(request):
    lists = ValidationLists.objects.filter(is_deleted=False).values()
    return JsonResponse(list(lists), safe=False)


# Create
@csrf_exempt
def validation_list_create(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        obj = ValidationLists.objects.create(
            listname=data.get("listname"),
            listvalue=data.get("listvalue"),
            createdby=request.user if request.user.is_authenticated else None,
        )
        return JsonResponse({"id": obj.list_id, "message": "Created"}, status=201)


# Update
@csrf_exempt
def validation_list_update(request, list_id):
    try:
        obj = ValidationLists.objects.get(pk=list_id, is_deleted=False)
    except ValidationLists.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method == "PUT" or request.method == "PATCH":
        data = json.loads(request.body.decode("utf-8"))
        obj.listname = data.get("listname", obj.listname)
        obj.listvalue = data.get("listvalue", obj.listvalue)
        obj.updated = timezone.now()
        obj.updatedby = request.user if request.user.is_authenticated else None
        obj.save()
        return JsonResponse({"message": "Updated"})
    return JsonResponse({"error": "Invalid method"}, status=405)


# Delete (soft delete)
@csrf_exempt
def validation_list_delete(request, list_id):
    try:
        obj = ValidationLists.objects.get(pk=list_id, is_deleted=False)
    except ValidationLists.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method == "DELETE":
        obj.is_deleted = True
        obj.save()
        return JsonResponse({"message": "Deleted"})
    return JsonResponse({"error": "Invalid method"}, status=405)
