
import json
import jwt
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail

from .models import Employee
from Approvals.models import SignupRequest
from Common.Middleware import authenticate, restrict
from Company.models import Company
from Users.models import UserRole
from EmailDomain.models import EmailDomain
from .utils.otp_utils import send_email_otp, generate_otp, otp_expired



# 🔹 JWT Generator
def generate_jwt(employee):
    payload = {
        "user_id": employee.emp_id,   # required for compatibility
        "emp_id": employee.emp_id,
        "email": employee.email,
        "role": employee.role.role_name if employee.role else None,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


# 🔹 Register Employee
@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        emp_name = data.get("emp_name")
        company_name = data.get("company_name")
        description = data.get("description")
        role_name = data.get("role")  # passed from frontend
        phone_number = data.get("ph_number")  # 👈 new field from frontend
        designation = data.get("designation")

        # ✅ Basic validations
        if not email or not password:
            return JsonResponse({"error": "email and password are required"}, status=400)
        if not phone_number:
            return JsonResponse({"error": "phone number is required"}, status=400)

        # ✅ Check email domain
        domain = email.split("@")[-1].lower()
        if not EmailDomain.objects.filter(domain_name=domain, is_deleted=False).exists():
            return JsonResponse(
                {"error": f"Email domain '{domain}' is not allowed"}, status=400
            )

        # ✅ Check duplicate email among active users only
        if Employee.objects.filter(email=email, is_deleted=False).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        # ✅ Find company
        try:
            company = Company.objects.get(company_name=company_name)
        except Company.DoesNotExist:
            return JsonResponse({"error": "Company not found"}, status=404)

        # ✅ Find role (if provided)
        role = None
        if role_name:
            try:
                role = UserRole.objects.get(role_name=role_name)
            except UserRole.DoesNotExist:
                return JsonResponse({"error": f"Role '{role_name}' not found"}, status=404)

        # ✅ Admin creating employee?
        creator_emp = None
        if hasattr(request, "Employee") and request.user.get("emp_id"):
            creator_emp = Employee.objects.filter(
                emp_id=request.user["emp_id"], is_deleted=False
            ).first()

        # ✅ Create employee (unverified)
        employee = Employee.objects.create(
            email=email,
            emp_name=emp_name,
            phone_number=phone_number,
            description=description,
            password=make_password(password),
            company_name=company,
            role=role,
            designation=designation,
            is_email_verified=False,
            createdby=creator_emp if creator_emp else None,
            updatedby=creator_emp if creator_emp else None,
        )

        # ✅ Self-register fallback
        if not creator_emp:
            employee.createdby = employee
            employee.updatedby = employee
            employee.save()
        
        email_otp = generate_otp()
        # phone_otp = generate_otp()
        employee.email_otp = email_otp
        employee.email_otp_created = datetime.datetime.now()
        # employee.phone_otp = phone_otp
        # employee.phone_otp_created = datetime.datetime.now()
        employee.save()
        # ✅ Send OTPs (async recommended in production)
        send_email_otp(employee.email,email_otp)
        # send_sms_otp(employee.email,phone_otp)

        # ✅ Response
        return JsonResponse({
            "message": "Registration successful. OTPs sent to email and phone. Please verify before login.",
            "emp_id": employee.emp_id,
            "email": employee.email,
            "phone_number": employee.phone_number,
            "emp_name": employee.emp_name,
            "company_name": employee.company_name.company_name if employee.company_name else None,
            "role": employee.role.role_name if employee.role else None,
            "description": employee.description,
            "is_email_verified": employee.is_email_verified,
            # "is_phone_verified": employee.is_phone_verified,
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        # if not employee.is_email_verified or not employee.is_phone_verified:
        #     return JsonResponse({"error": "Please verify email and phone before login"}, status=403)

        if not email or not password:
            return JsonResponse({"error": "email and password are required"}, status=400)

        employee = Employee.objects.filter(
            email=email, is_deleted=False).first()
        if not employee or not check_password(password, employee.password):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        token = generate_jwt(employee)

        return JsonResponse({
            "message": "Login successful",
            "token": token,
            "emp_id": employee.emp_id,
            "emp_name": employee.emp_name if employee.emp_name else None,
            "email": employee.email if employee.email else None,
            "company_name": employee.company_name.company_name if employee.company_name else None,
            "role": employee.role.role_name if employee.role else None,
            "designation": employee.designation if employee.designation else None,
      },status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
def verify_email_otp(request):
    data = json.loads(request.body)
    email = data.get("email")
    otp = data.get("otp")
    print(email, otp)

    employee = Employee.objects.filter(email=email, is_deleted=False).first()
    if not employee:
        return JsonResponse({"error": "User not found"}, status=404)

    if employee.is_email_verified:
        return JsonResponse({"message": "Already verified"}, status=200)

    if otp != employee.email_otp or otp_expired(employee.email_otp_created):
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

    employee.is_email_verified = True
    employee.email_otp = None
    employee.save()
    return JsonResponse({"message": "Email verified successfully"}, status=200)

@csrf_exempt
def verify_phone_otp(request):
    data = json.loads(request.body)
    phone = data.get("phone")
    otp = data.get("otp")

    employee = Employee.objects.filter(phone_number=phone, is_deleted=False).first()
    if not employee:
        return JsonResponse({"error": "User not found"}, status=404)

    if employee.is_phone_verified:
        return JsonResponse({"message": "Already verified"}, status=200)

    if otp != employee.phone_otp or otp_expired(employee.phone_otp_created):
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

    employee.is_phone_verified = True
    employee.phone_otp = None
    employee.save()
    return JsonResponse({"message": "Phone verified successfully"}, status=200)


# 🔹 Forgot Password - Request OTP
@csrf_exempt
def request_password_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        employee = Employee.objects.filter(email=email, is_deleted=False).first()
        if not employee:
            # Don't reveal if email exists or not for security
            return JsonResponse({"message": "If the email exists, an OTP has been sent"}, status=200)

        # Generate and save OTP
        email_otp = generate_otp()
        employee.email_otp = email_otp
        employee.email_otp_created = datetime.datetime.now()
        employee.save()

        # Send OTP via email
        send_email_otp(employee.email, email_otp)

        return JsonResponse({"message": "OTP sent to your email"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 🔹 Forgot Password - Verify OTP
@csrf_exempt
def verify_password_reset_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        otp = data.get("otp")

        if not email or not otp:
            return JsonResponse({"error": "Email and OTP are required"}, status=400)

        employee = Employee.objects.filter(email=email, is_deleted=False).first()
        if not employee:
            return JsonResponse({"error": "User not found"}, status=404)

        if not employee.email_otp or otp != employee.email_otp:
            return JsonResponse({"error": "Invalid OTP"}, status=400)

        if otp_expired(employee.email_otp_created):
            return JsonResponse({"error": "OTP has expired"}, status=400)

        # OTP verified successfully - allow password reset
        return JsonResponse({"message": "OTP verified successfully"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 🔹 Forgot Password - Reset Password
@csrf_exempt
def reset_password(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        otp = data.get("otp")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not email or not otp or not new_password or not confirm_password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        employee = Employee.objects.filter(email=email, is_deleted=False).first()
        if not employee:
            return JsonResponse({"error": "User not found"}, status=404)

        # Verify OTP again before resetting
        if not employee.email_otp or otp != employee.email_otp:
            return JsonResponse({"error": "Invalid OTP"}, status=400)

        if otp_expired(employee.email_otp_created):
            return JsonResponse({"error": "OTP has expired"}, status=400)

        # Reset password
        employee.password = make_password(new_password)
        employee.email_otp = None  # Clear OTP after use
        employee.email_otp_created = None
        employee.save()

        return JsonResponse({"message": "Password reset successfully"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 🔹 List all Employees (Admin/SuperAdmin only)
@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def list_employees(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    employees = Employee.objects.filter(is_deleted=False)
    data = []
    for emp in employees:
        data.append({
            "emp_id": emp.emp_id,
            "email": emp.email,
            "emp_name": emp.emp_name,
            "role": emp.role.role_name if emp.role else None,
            "company": emp.company_name.company_name if emp.company_name else None,
            "created": emp.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "createdby": emp.createdby.emp_name if emp.createdby else None,
            "updated": emp.updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedby": emp.updatedby.emp_name if emp.updatedby else None,
        })

    return JsonResponse({"employees": data})


# 🔹 Update Employee (Admin only)
# 🔹 Update Employee (Admin only)
@csrf_exempt
@authenticate
# @restrict(roles=['Admin'])
def update_employee(request, emp_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        employee = Employee.objects.get(emp_id=emp_id, is_deleted=False)
    except Employee.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        role_name = data.get("role")
        company_name = data.get("company_name")
        emp_name = data.get("emp_name")

        # 🔹 Update email and password
        if email:
            employee.email = email
        if password:
            employee.password = make_password(password)

        # 🔹 Safely update role (handle duplicates)
        if role_name:
            role = UserRole.objects.filter(role_name=role_name).first()
            if not role:
                return JsonResponse({"error": "Role not found"}, status=404)
            employee.role = role

        # 🔹 Update company (except for SuperAdmin)
        if company_name and (not employee.role or employee.role.role_name.lower() != "superadmin"):
            company = Company.objects.filter(company_name=company_name).first()
            if not company:
                return JsonResponse({"error": "Company not found"}, status=404)
            employee.company_name = company

        # 🔹 Track who updated the employee
        updater = None
        if hasattr(request, "user") and request.user.get("emp_id"):
            updater = Employee.objects.filter(
                emp_id=request.user["emp_id"], is_deleted=False
            ).first()

        employee.updated = datetime.datetime.now()
        employee.emp_name = emp_name
        if updater:
            employee.updatedby = updater

        employee.save()

        return JsonResponse({
            "message": "Employee updated successfully",
            "emp_id": employee.emp_id,
            "email": employee.email,
            "role": employee.role.role_name if employee.role else None,
            "company_name": employee.company_name.company_name if employee.company_name else None
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


# 🔹 Send Registration Invite (Admin/SuperAdmin only)
@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def send_registration_invite(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # If already an active employee, do not send invite
        if Employee.objects.filter(email=email, is_deleted=False).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        # Build registration URL (fallback to localhost if not provided)
        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None)
        if not frontend_base:
            frontend_base = "http://localhost:3000"
        registration_link = f"{frontend_base}/signup?email={email}"

        subject = "Complete your registration"
        message = (
            "You have been invited to register your account.\n\n"
            f"Please click the link below to complete your registration:\n{registration_link}\n\n"
            "If you did not expect this email, you can ignore it."
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({"message": "Registration link sent"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# 🔹 Delete Employee (Admin/SuperAdmin only)
@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def delete_employee(request, emp_id):
    if request.method == "DELETE":
        try:
            employee = Employee.objects.get(emp_id=emp_id, is_deleted=False)
            employee.is_deleted = True
            employee.save()
            return JsonResponse({"message": "Employee deleted successfully"}, status=200)
        except Employee.DoesNotExist:
            return JsonResponse({"message": "Employee not found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    return JsonResponse({"message": "Method Not Allowed"}, status=405)

# 🔹 List employees with no role (Admin/SuperAdmin only)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def list_employees_without_role(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    employees = Employee.objects.filter(is_deleted=False, role__isnull=True)
    data = []
    for emp in employees:
        data.append({
            "emp_id": emp.emp_id,
            "email": emp.email,
            "emp_name": emp.emp_name,
            "company": emp.company_name.company_name if emp.company_name else None,

        })

    return JsonResponse({"employees_without_role": data}, status=200)

# 🔹 Assign role to employee (Admin/SuperAdmin only)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def assign_role(request, emp_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        employee = Employee.objects.get(emp_id=emp_id, is_deleted=False)
    except Employee.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)

    try:
        data = json.loads(request.body)
        role_name = data.get("role")

        if not role_name:
            return JsonResponse({"error": "Role name is required"}, status=400)

        try:
            role = UserRole.objects.filter(role_name=role_name).first()
            if not role:
                return JsonResponse({"error": "Role not found"}, status=404)
        except UserRole.DoesNotExist:
            return JsonResponse({"error": "Role not found"}, status=404)

        employee.role = role
        employee.save()

        return JsonResponse({
            "message": "Role assigned successfully",
            "emp_id": employee.emp_id,
            "emp_name": employee.emp_name,
            "email": employee.email,
            "role": employee.role.role_name
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

# 🔹 Assign role to multiple employees (Admin/SuperAdmin only)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def bulk_assign_roles(request):
    if request.method != "PUT":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        emp_ids = data.get("emp_ids", [])   # list of employee IDs
        role_name = data.get("role")

        if not emp_ids or not isinstance(emp_ids, list):
            return JsonResponse({"error": "emp_ids (list) is required"}, status=400)
        if not role_name:
            return JsonResponse({"error": "Role name is required"}, status=400)

        try:
            role = UserRole.objects.filter(role_name=role_name).first()
            if not role:
                return JsonResponse({"error": "Role not found"}, status=404)
        except UserRole.DoesNotExist:
            return JsonResponse({"error": "Role not found"}, status=404)

        updated_employees = []
        for emp_id in emp_ids:
            try:
                employee = Employee.objects.get(
                    emp_id=emp_id, is_deleted=False)
                employee.role = role
                employee.save()
                updated_employees.append({
                    "emp_id": employee.emp_id,
                    "emp_name": employee.emp_name,
                    "email": employee.email,
                    "role": employee.role.role_name
                })
            except Employee.DoesNotExist:
                continue  # skip missing employees

        return JsonResponse({
            "message": f"Role '{role_name}' assigned to {len(updated_employees)} employees",
            "updated_employees": updated_employees
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
