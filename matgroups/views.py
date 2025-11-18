from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from .models import MatGroup
from supergroups.models import SuperGroup
from Employee.models import Employee
from Common.Middleware import authenticate, restrict


# ✅ Helper to get employee name
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ✅ CREATE MatGroup
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin","MDGT"])
def create_matgroup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            mgrp_code = data.get("mgrp_code")
            sgrp_code = data.get("sgrp_code",None)
            mgrp_shortname = data.get("mgrp_shortname",None)
            mgrp_longname = data.get("mgrp_longname",None)
            search_type = data.get("search_type", "Materials")
            attribgrpid = data.get("attribgrpid", None)
            notes = data.get("notes", "")

            if not mgrp_code:
                return JsonResponse({"error": "Required fields: mgrp_code, sgrp_code, mgrp_shortname, mgrp_longname"}, status=400)

            # ✅ Check if SuperGroup exists
            supergroup = SuperGroup.objects.filter(sgrp_code=sgrp_code, is_deleted=False).first()
            # if not supergroup:
            #     return JsonResponse({"error": "SuperGroup not found"}, status=404)

            # ✅ Handle attribgrpid if provided
            attribgrp_obj = None
            if attribgrpid:
                from matg_attributes.models import MatgAttributeItem
                attribgrp_obj = MatgAttributeItem.objects.filter(id=attribgrpid, is_deleted=False).first()

            # ✅ Get Employee for createdby
            emp_id = request.user.get("emp_id")
            createdby = Employee.objects.filter(emp_id=emp_id).first()

            matgroup = MatGroup.objects.create(
                mgrp_code=mgrp_code,
                sgrp_code=supergroup,
                search_type=search_type,
                mgrp_shortname=mgrp_shortname,
                mgrp_longname=mgrp_longname,
                attribgrpId=attribgrp_obj,
                notes=notes,
                createdby=createdby,
                updatedby=createdby
            )

            response_data = {
                "mgrp_code": matgroup.mgrp_code,
                "mgrp_shortname": matgroup.mgrp_shortname,
                "mgrp_longname": matgroup.mgrp_longname,
                "search_type": matgroup.search_type,
                "attribgrpid": matgroup.attribgrpId.id if matgroup.attribgrpId else None,
                "notes": matgroup.notes,
                "supergroup": matgroup.sgrp_code.sgrp_name if matgroup.sgrp_code else None,
                "created": matgroup.created.strftime("%Y-%m-%d %H:%M:%S") if matgroup.created else None,
                "updated": matgroup.updated.strftime("%Y-%m-%d %H:%M:%S") if matgroup.updated else None,
                "createdby": get_employee_name(matgroup.createdby),
                "updatedby": get_employee_name(matgroup.updatedby)
            }
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ✅ LIST MatGroups
@authenticate
@restrict(roles=["Admin", "SuperAdmin", "User","MDGT"])
def list_matgroups(request):
    if request.method == "GET":
        try:
            matgroups = MatGroup.objects.filter(is_deleted=False)
            response_data = []
            for mg in matgroups:
                response_data.append({
                    "mgrp_code": mg.mgrp_code,
                    "mgrp_shortname": mg.mgrp_shortname,
                    "mgrp_longname": mg.mgrp_longname,
                    "search_type": mg.search_type,
                    "attribgrpid": mg.attribgrpId.id if mg.attribgrpId else None,
                    "notes": mg.notes,
                    "supergroup": mg.sgrp_code.sgrp_name if mg.sgrp_code else None,
                    "created": mg.created.strftime("%Y-%m-%d %H:%M:%S") if mg.created else None,
                    "updated": mg.updated.strftime("%Y-%m-%d %H:%M:%S") if mg.updated else None,
                    "createdby": get_employee_name(mg.createdby),
                    "updatedby": get_employee_name(mg.updatedby)
                })
            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)


# ✅ UPDATE MatGroup
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin","MDGT"])
def update_matgroup(request, mgrp_code):
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))

            matgroup = MatGroup.objects.filter(mgrp_code=mgrp_code, is_deleted=False).first()
            if not matgroup:
                return JsonResponse({"error": "MatGroup not found"}, status=404)

            # ✅ Update fields
            matgroup.mgrp_shortname = data.get("mgrp_shortname", matgroup.mgrp_shortname)
            matgroup.mgrp_longname = data.get("mgrp_longname", matgroup.mgrp_longname)
            matgroup.search_type = data.get("search_type", matgroup.search_type)
            # Handle attribgrpid update if provided
            attribgrpid = data.get("attribgrpid")
            if attribgrpid is not None:
                from matg_attributes.models import MatgAttributeItem
                attribgrp_obj = MatgAttributeItem.objects.filter(id=attribgrpid, is_deleted=False).first() if attribgrpid else None
                matgroup.attribgrpId = attribgrp_obj
            matgroup.notes = data.get("notes", matgroup.notes)

            # ✅ If sgrp_code is updated
            new_sgrp_code = data.get("sgrp_code")
            if new_sgrp_code:
                supergroup = SuperGroup.objects.filter(sgrp_code=new_sgrp_code, is_deleted=False).first()
                if not supergroup:
                    return JsonResponse({"error": "SuperGroup not found"}, status=404)
                matgroup.sgrp_code = supergroup

            # ✅ Update audit
            emp_id = request.user.get("emp_id")
            updatedby = Employee.objects.filter(emp_id=emp_id).first()
            matgroup.updatedby = updatedby
            matgroup.updated = timezone.now()

            matgroup.save()

            response_data = {
                "mgrp_code": matgroup.mgrp_code,
                "mgrp_shortname": matgroup.mgrp_shortname,
                "mgrp_longname": matgroup.mgrp_longname,
                "search_type": matgroup.search_type,
                "attribgrpid": matgroup.attribgrpId.id if matgroup.attribgrpId else None,
                "notes": matgroup.notes,
                "supergroup": matgroup.sgrp_code.sgrp_name if matgroup.sgrp_code else None,
                "created": matgroup.created.strftime("%Y-%m-%d %H:%M:%S") if matgroup.created else None,
                "updated": matgroup.updated.strftime("%Y-%m-%d %H:%M:%S") if matgroup.updated else None,
                "createdby": get_employee_name(matgroup.createdby),
                "updatedby": get_employee_name(matgroup.updatedby)
            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ✅ HARD DELETE MatGroup
@csrf_exempt
@authenticate
@restrict(roles=["Admin", "SuperAdmin","MDGT"])
def delete_matgroup(request, mgrp_code):
    if request.method == "DELETE":
        matgroup = MatGroup.objects.filter(mgrp_code=mgrp_code).first()
        if not matgroup:
            return JsonResponse({"error": "MatGroup not found"}, status=404)

        matgroup.delete()  # ✅ Hard delete
        return JsonResponse({"message": "MatGroup deleted successfully"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)
