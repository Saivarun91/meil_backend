import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Request
from Employee.models import Employee
from itemmaster.models import ItemMaster
from Common.Middleware import authenticate, restrict
# ✅ Get Project object
from projects.models import Project
from matgroups.models import MatGroup


# ✅ Helper function to get employee name
def get_employee_name(emp):
    return emp.emp_name if emp else None


# ===========================
# CREATE Request
# ===========================
# ===========================
# CREATE Request (only project_id & notes)
# ===========================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def create_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            project_code = data.get("project_code")
            print(project_code)
            notes = data.get("notes", "")
            request_type = data.get("type", "")

            if not project_code:
                return JsonResponse({"error": "project_id is required"}, status=400)

            # ✅ Get Employee for createdby
            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=400)

            project_obj = Project.objects.filter(
                project_code=project_code).first()
            if not project_obj:
                return JsonResponse({"error": f"Project with id={project_code} not found"}, status=404)

            # ✅ Create Request
            request_obj = Request.objects.create(
                project_code=project_obj,
                notes=notes,
                type=request_type,
                createdby=employee,
                updatedby=employee,
                isread=True,  # New requests start as read (no messages yet)
                tobeshown=None  # No message to show yet
            )

            response_data = {
                "request_id": request_obj.request_id,
                "project_code": request_obj.project_code.project_code if request_obj.project_code else None,
                "project_name": request_obj.project_code.project_name if request_obj.project_code else None,
                "notes": request_obj.notes,
                "type": request_obj.type,
                "request_status": request_obj.request_status,
                "created": request_obj.created.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(request_obj.createdby)
            }

            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ===========================
# LIST Requests
# ===========================
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "Employee", "MDGT"])
def list_requests(request):
    if request.method == "GET":
        try:
            requests_qs = Request.objects.filter(is_deleted=False)
            # Employees see only their own requests; MDGT/Admin/SuperAdmin see all
            try:
                user_role = request.user.get("role") if isinstance(
                    request.user, dict) else None
                if user_role == "Employee":
                    emp_id = request.user.get("emp_id")
                    employee = Employee.objects.filter(emp_id=emp_id).first()
                    if employee:
                        requests_qs = requests_qs.filter(createdby=employee)
            except Exception:
                pass
            # Get current user info for unread calculation
            emp_id = request.user.get("emp_id")
            current_employee = Employee.objects.filter(emp_id=emp_id).first()
            user_role = request.user.get("role") if isinstance(
                request.user, dict) else None
            if not user_role and current_employee and current_employee.role:
                user_role = current_employee.role.role_name

            response_data = []
            for r in requests_qs:
                # Calculate unread count for this request
                unread_count = 0
                is_unread = False

                if r.isread == False and r.tobeshown:
                    # Get the last message from chat
                    chat_messages = r.request_data.get(
                        "chat", []) if r.request_data else []
                    if chat_messages:
                        last_message = chat_messages[-1]
                        last_sender_role = last_message.get("sender_role")
                        last_sender_emp_id = last_message.get("sender_emp_id")

                        # Fallback: find by name if role not stored in message
                        if not last_sender_role:
                            last_sender_name = last_message.get("sender", "")
                            last_sender_emp = Employee.objects.filter(
                                emp_name=last_sender_name, is_deleted=False).first()
                            if last_sender_emp and last_sender_emp.role:
                                last_sender_role = last_sender_emp.role.role_name
                                last_sender_emp_id = last_sender_emp.emp_id

                        if last_sender_role and current_employee:
                            # Determine if current user should see this as unread
                            if user_role == "MDGT" or user_role == "Admin" or user_role == "SuperAdmin":
                                # MDGT should see unread if last message was from an Employee (not MDGT/Admin/SuperAdmin)
                                # AND the message is not from themselves
                                if (last_sender_role != "MDGT" and last_sender_role != "Admin" and last_sender_role != "SuperAdmin") and last_sender_emp_id != current_employee.emp_id:
                                    is_unread = True
                                    unread_count = 1
                            else:
                                # Employee should see unread if:
                                # 1. They created the request AND
                                # 2. Last message was from MDGT/Admin/SuperAdmin AND
                                # 3. The message is not from themselves
                                if (r.createdby == current_employee and
                                    (last_sender_role == "MDGT" or last_sender_role == "Admin" or last_sender_role == "SuperAdmin") and
                                        last_sender_emp_id != current_employee.emp_id):
                                    is_unread = True
                                    unread_count = 1

                response_data.append({
                    "request_id": r.request_id,
                    "request_date": r.request_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "request_status": r.request_status,
                    "project_code": r.project_code.project_code if r.project_code else None,
                    "project_name": r.project_code.project_name if r.project_code else None,

                    "user_text": r.request_data,

                    "sap_item": r.sap_item.sap_item_id if r.sap_item else None,
                    "material_group": r.material_group.mgrp_code if r.material_group else None,
                    "notes": r.notes,
                    "type": r.type,
                    "closetime": r.closetime.strftime("%Y-%m-%d") if r.closetime else None,
                    "status": r.status,
                    "timetaken": r.timetaken,
                    "created": r.created.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated": r.updated.strftime("%Y-%m-%d %H:%M:%S"),
                    "createdby": get_employee_name(r.createdby),
                    "updatedby": get_employee_name(r.updatedby),
                    "isread": r.isread,
                    "tobeshown": r.tobeshown.strftime("%Y-%m-%d %H:%M:%S") if r.tobeshown else None,
                    "unread_count": unread_count,
                    "is_unread": is_unread
                })
            return JsonResponse(response_data, safe=False, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ===========================
# UPDATE Request
# ===========================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT", "Employee"])
def update_request(request, request_id):
    if request.method == "PUT":
        try:
            req_obj = Request.objects.filter(
                request_id=request_id, is_deleted=False).first()
            if not req_obj:
                return JsonResponse({"error": "Request not found"}, status=404)

            data = json.loads(request.body.decode("utf-8"))

            # Prevent any updates if request is closed
            if req_obj.status and req_obj.status.lower() == "closed":
                # Allow status change from closed to open, but prevent other field updates
                requested_status = data.get("status", req_obj.status)
                if requested_status and requested_status.lower() != "closed":
                    # Allow reopening the request
                    req_obj.status = requested_status
                    req_obj.updated = timezone.now()
                    emp_id = request.user.get("emp_id")
                    employee = Employee.objects.filter(emp_id=emp_id).first()
                    if employee:
                        req_obj.updatedby = employee
                    req_obj.save()
                    return JsonResponse({
                        "request_id": req_obj.request_id,
                        "status": req_obj.status,
                        "message": "Request reopened"
                    }, status=200)
                else:
                    return JsonResponse({"error": "Cannot update closed request. Reopen the request first to make changes."}, status=400)

            # Update fields if provided
            req_obj.notes = data.get("notes", req_obj.notes)
            closetime_str = data.get("closetime")
            if closetime_str:
                try:
                    req_obj.closetime = datetime.strptime(
                        closetime_str, "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"error": "closetime must be in YYYY-MM-DD format"}, status=400)

            sap_item_value = data.get("sap_item")
            if sap_item_value:
                try:
                    req_obj.sap_item = ItemMaster.objects.get(
                        sap_item_id=sap_item_value)
                except ItemMaster.DoesNotExist:
                    return JsonResponse({"error": f"ItemMaster with sap_item_id={sap_item_value} not found"}, status=404)

            # Validate closing rules for MDGT: cannot close without SAP item
            requested_status = data.get("status", req_obj.status)
            try:
                user_role = request.user.get("role") if isinstance(
                    request.user, dict) else None
                if requested_status == "Closed" and user_role == "MDGT":
                    sap_item_in_payload = data.get("sap_item")
                    if not (req_obj.sap_item or sap_item_in_payload):
                        return JsonResponse({"error": "SAP Item is required to close this request"}, status=400)
            except Exception:
                pass

            req_obj.status = requested_status
            req_obj.timetaken = data.get("timetaken", req_obj.timetaken)
            req_obj.request_status = data.get(
                "request_status", req_obj.request_status)
            req_obj.reply_emaildate = data.get(
                "reply_emaildate", req_obj.reply_emaildate)
            req_obj.reply_smsdate = data.get(
                "reply_smsdate", req_obj.reply_smsdate)

            # ✅ Update audit
            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=400)

            req_obj.updatedby = employee
            req_obj.updated = timezone.now()
            req_obj.save()

            response_data = {
                "request_id": req_obj.request_id,
                "request_status": req_obj.request_status,

                "sap_item": req_obj.sap_item.sap_item_id if req_obj.sap_item else None,
                "notes": req_obj.notes,
                "closetime": req_obj.closetime.strftime("%Y-%m-%d") if req_obj.closetime else None,
                "status": req_obj.status,
                "timetaken": req_obj.timetaken,
                "created": req_obj.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": req_obj.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "createdby": get_employee_name(req_obj.createdby),
                "updatedby": get_employee_name(req_obj.updatedby)
            }
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ===========================
# DELETE Request (Hard Delete)
# ===========================
@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT"])
def delete_request(request, request_id):
    if request.method == "DELETE":
        req_obj = Request.objects.filter(request_id=request_id).first()
        if not req_obj:
            return JsonResponse({"error": "Request not found"}, status=404)

        req_obj.delete()  # ✅ Hard delete
        return JsonResponse({"message": f"Request {request_id} deleted successfully"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# ===========================
# ASSIGN SAP ITEM (only MDGT)
# ===========================


@csrf_exempt
@authenticate
# @restrict(roles=["MDGT"])
def assign_sap_item(request, request_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))
            sap_item_value = data.get("sap_item")

            if not sap_item_value:
                return JsonResponse({"error": "sap_item is required"}, status=400)

            req_obj = Request.objects.filter(
                request_id=request_id, is_deleted=False).first()
            if not req_obj:
                return JsonResponse({"error": "Request not found"}, status=404)

            # Prevent updates if request is closed
            if req_obj.status and req_obj.status.lower() == "closed":
                return JsonResponse({"error": "Cannot update SAP Item: Request is closed"}, status=400)

            try:
                sap_item_obj = ItemMaster.objects.get(
                    sap_item_id=sap_item_value)
            except ItemMaster.DoesNotExist:
                return JsonResponse({"error": f"ItemMaster with sap_item_id={sap_item_value} not found"}, status=404)

            req_obj.sap_item = sap_item_obj
            # Do not auto-close - allow changes until manually closed
            req_obj.updated = timezone.now()

            # ✅ Update audit
            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            req_obj.updatedby = employee

            req_obj.save()

            response_data = {
                "request_id": req_obj.request_id,
                "project_code": req_obj.project_code.project_code if req_obj.project_code else None,
                "sap_item": req_obj.sap_item.sap_item_id if req_obj.sap_item else None,
                "request_status": req_obj.request_status,
                "updated": req_obj.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "updatedby": get_employee_name(req_obj.updatedby)
            }
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ===========================
# ASSIGN MATERIAL GROUP (only MDGT)
# ===========================
@csrf_exempt
@authenticate
# @restrict(roles=["MDGT"])
def assign_material_group(request, request_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode("utf-8"))
            material_group_code = data.get("material_group")

            if not material_group_code:
                return JsonResponse({"error": "material_group is required"}, status=400)

            req_obj = Request.objects.filter(
                request_id=request_id, is_deleted=False).first()
            if not req_obj:
                return JsonResponse({"error": "Request not found"}, status=404)

            # Prevent updates if request is closed
            if req_obj.status and req_obj.status.lower() == "closed":
                return JsonResponse({"error": "Cannot update Material Group: Request is closed"}, status=400)

            try:
                mat_group_obj = MatGroup.objects.get(
                    mgrp_code=material_group_code, is_deleted=False)
            except MatGroup.DoesNotExist:
                return JsonResponse({"error": f"MatGroup with mgrp_code={material_group_code} not found"}, status=404)

            req_obj.material_group = mat_group_obj
            # Do not auto-close - allow changes until manually closed
            req_obj.updated = timezone.now()

            # ✅ Update audit
            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            req_obj.updatedby = employee

            req_obj.save()

            response_data = {
                "request_id": req_obj.request_id,
                "project_code": req_obj.project_code.project_code if req_obj.project_code else None,
                "material_group": req_obj.material_group.mgrp_code if req_obj.material_group else None,
                "request_status": req_obj.request_status,
                "updated": req_obj.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "updatedby": get_employee_name(req_obj.updatedby)
            }
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT", "Employee"])
def add_chat_message(request, request_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        message_text = data.get("message")
        if not message_text:
            return JsonResponse({"error": "message is required"}, status=400)

        req_obj = Request.objects.filter(
            request_id=request_id, is_deleted=False).first()
        if not req_obj:
            return JsonResponse({"error": "Request not found"}, status=404)

        emp_id = request.user.get("emp_id")
        employee = Employee.objects.filter(emp_id=emp_id).first()
        if not employee:
            return JsonResponse({"error": "Employee not found"}, status=404)

        # Ensure request_data is a dict
        if not isinstance(req_obj.request_data, dict):
            req_obj.request_data = {}

        # Ensure 'chat' key is a list
        if "chat" not in req_obj.request_data or not isinstance(req_obj.request_data.get("chat"), list):
            req_obj.request_data["chat"] = []

        # Append new chat message
        current_time = timezone.now()
        req_obj.request_data["chat"].append({
            "sender": employee.emp_name,
            "message": message_text,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
        })

        # Update isread and tobeshown based on sender role
        # When user sends message: set for MDGT to see
        # When MDGT sends message: set for the user who created the request to see
        # Always mark as unread when a new message is sent
        req_obj.isread = False
        req_obj.tobeshown = current_time

        # Also store sender info in the message for easier lookup
        req_obj.request_data["chat"][-1]["sender_emp_id"] = employee.emp_id
        if employee.role:
            req_obj.request_data["chat"][-1]["sender_role"] = employee.role.role_name

        # Save JSONB
        req_obj.updatedby = employee
        req_obj.updated = current_time
        req_obj.save()

        # Broadcast to WebSocket group for this request
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            group_name = f"chat_{request_id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat.message",  # maps to ChatConsumer.chat_message
                    "message": {
                        "sender": employee.emp_name,
                        "message": message_text,
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                },
            )
        except Exception:
            # Fallback silently if WS not configured
            pass

        return JsonResponse({"message": "Chat message added successfully", "request_data": req_obj.request_data}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print("Error in add_chat_message:", e)
        return JsonResponse({"error": str(e)}, status=500)


@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT", "Employee"])
def list_chat_messages(request, request_id):
    if request.method == "GET":
        try:
            req_obj = Request.objects.filter(
                request_id=request_id, is_deleted=False).first()
            if not req_obj:
                return JsonResponse({"error": "Request not found"}, status=404)

            chat_messages = req_obj.request_data.get(
                "chat", []) if req_obj.request_data else []

            return JsonResponse(chat_messages, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT", "Employee"])
def get_unread_count(request):
    if request.method == "GET":
        try:
            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=404)

            user_role = request.user.get("role") if isinstance(
                request.user, dict) else None
            if not user_role and employee.role:
                user_role = employee.role.role_name

            # Get all requests with unread messages
            requests_qs = Request.objects.filter(
                is_deleted=False, isread=False, tobeshown__isnull=False)

            unread_count = 0

            for req in requests_qs:
                # Get the last message from chat
                chat_messages = req.request_data.get(
                    "chat", []) if req.request_data else []
                if not chat_messages:
                    continue

                last_message = chat_messages[-1]

                # Try to get sender role from message first (more reliable)
                last_sender_role = last_message.get("sender_role")
                last_sender_emp_id = last_message.get("sender_emp_id")

                # Fallback: find by name if role not stored in message
                if not last_sender_role:
                    last_sender_name = last_message.get("sender", "")
                    last_sender_emp = Employee.objects.filter(
                        emp_name=last_sender_name, is_deleted=False).first()
                    if last_sender_emp and last_sender_emp.role:
                        last_sender_role = last_sender_emp.role.role_name
                        last_sender_emp_id = last_sender_emp.emp_id

                if not last_sender_role:
                    continue

                # Determine if current user should see this as unread
                if user_role == "MDGT" or user_role == "Admin" or user_role == "SuperAdmin":
                    # MDGT should see unread if last message was from an Employee (not MDGT/Admin/SuperAdmin)
                    # AND the message is not from themselves
                    if (last_sender_role != "MDGT" and last_sender_role != "Admin" and last_sender_role != "SuperAdmin") and last_sender_emp_id != employee.emp_id:
                        unread_count += 1
                else:
                    # Employee should see unread if:
                    # 1. They created the request AND
                    # 2. Last message was from MDGT/Admin/SuperAdmin AND
                    # 3. The message is not from themselves
                    if (req.createdby == employee and
                        (last_sender_role == "MDGT" or last_sender_role == "Admin" or last_sender_role == "SuperAdmin") and
                            last_sender_emp_id != employee.emp_id):
                        unread_count += 1

            return JsonResponse({"unread_count": unread_count}, status=200)

        except Exception as e:
            print(f"Error in get_unread_count: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=["Admin", "SuperAdmin", "MDGT", "Employee"])
def mark_request_read(request, request_id):
    if request.method == "PUT":
        try:
            req_obj = Request.objects.filter(
                request_id=request_id, is_deleted=False).first()
            if not req_obj:
                return JsonResponse({"error": "Request not found"}, status=404)

            emp_id = request.user.get("emp_id")
            employee = Employee.objects.filter(emp_id=emp_id).first()
            if not employee:
                return JsonResponse({"error": "Employee not found"}, status=404)

            # Mark as read
            req_obj.isread = True
            req_obj.save()

            return JsonResponse({"message": "Request marked as read", "request_id": request_id}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
