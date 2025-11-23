# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.utils import timezone
# from django.shortcuts import get_object_or_404
# import json
# from .models import UserRole
# from Common.Middleware import authenticate,restrict
#   # Assuming you saved these decorators in middleware.py


# # ✅ LIST User Roles
# @csrf_exempt
# @authenticate
# # @restrict(roles=['Admin', 'SuperAdmin'])
# def userrole_list(request):
#     if request.method == 'GET':
#         roles = UserRole.objects.filter(is_deleted=False).order_by('role_priority')
#         data = [
#             {
#                 'userrole_id': role.userrole_id,
#                 'role_name': role.role_name,
#                 'role_priority': role.role_priority,
#                 'created': role.created.strftime('%Y-%m-%d %H:%M:%S'),
#                 'updated': role.updated.strftime('%Y-%m-%d %H:%M:%S')
#             } for role in roles
#         ]
#         return JsonResponse({'roles': data}, status=200)


# # ✅ CREATE User Role
# @csrf_exempt
# @authenticate
# # @restrict(roles=['Admin', 'SuperAdmin'])
# def userrole_create(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             role_name = data.get('role_name')
#             role_priority = data.get('role_priority')

#             if not role_name:
#                 return JsonResponse({'message': 'Role name is required'}, status=400)

#             userrole = UserRole.objects.create(
#                 role_name=role_name,
#                 role_priority=role_priority,
#                 createdby_id=request.user.get('emp_id'),
#                 updatedby_id=request.user.get('emp_id')
#             )
#             return JsonResponse({'message': 'User Role created successfully', 'id': userrole.userrole_id}, status=201)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)


# # ✅ UPDATE User Role
# @csrf_exempt
# @authenticate
# # @restrict(roles=['Admin', 'SuperAdmin'])
# def userrole_update(request, pk):
#     if request.method == 'PUT':
#         try:
#             userrole = get_object_or_404(UserRole, pk=pk, is_deleted=False)
#             data = json.loads(request.body)
#             role_name = data.get('role_name')
#             role_priority = data.get('role_priority')

#             if role_name:
#                 userrole.role_name = role_name
#             if role_priority:
#                 userrole.role_priority = role_priority

#             userrole.updated = timezone.now()
#             userrole.updatedby_id = request.user.get('emp_id')
#             userrole.save()

#             return JsonResponse({'message': 'User Role updated successfully'}, status=200)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)


# # ✅ DELETE User Role (Soft Delete)
# @csrf_exempt
# @authenticate
# # @restrict(roles=['Admin', 'SuperAdmin'])
# def userrole_delete(request, pk):
#     if request.method == 'DELETE':
#         try:
#             userrole = get_object_or_404(UserRole, pk=pk, is_deleted=False)
#             userrole.is_deleted = True
#             userrole.updated = timezone.now()
#             userrole.updatedby_id = request.user.get('emp_id')
#             userrole.save()

#             return JsonResponse({'message': 'User Role deleted successfully'}, status=200)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import UserRole
from Common.Middleware import authenticate, restrict
from django.db.models import Min


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def userrole_list(request):
    if request.method == 'GET':
        roles = (
            UserRole.objects
            .filter(is_deleted=False)
            .values('role_name')
            .annotate(primary_id=Min('userrole_id'))
            .order_by('role_name')
        )

        data = [
            {'id': r['primary_id'], 'role_name': r['role_name']}
            for r in roles if r['role_name']
        ]
        return JsonResponse({'roles': data}, status=200)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


# ✅ CREATE Role
@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def userrole_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            role_name = data.get('role_name')
            role_priority = data.get('role_priority')

            if not role_name:
                return JsonResponse({'message': 'Role name is required'}, status=400)

            userrole = UserRole.objects.create(
                role_name=role_name,
                role_priority=role_priority,
                createdby=None,  # No auth_user mapping
                updatedby=None,
                created_emp_id=request.user.get('emp_id'),
                updated_emp_id=request.user.get('emp_id')
            )
            return JsonResponse({'message': 'User Role created successfully', 'id': userrole.userrole_id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


# ✅ UPDATE Role
@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def userrole_update(request, pk):
    if request.method == 'PUT':
        try:
            userrole = get_object_or_404(UserRole, pk=pk)
            data = json.loads(request.body)
            role_name = data.get('role_name')
            role_priority = data.get('role_priority')

            if role_name:
                userrole.role_name = role_name
            if role_priority:
                userrole.role_priority = role_priority

            userrole.updated = timezone.now()
            userrole.updated_emp_id = request.user.get('emp_id')
            userrole.updatedby = None
            userrole.save()

            return JsonResponse({'message': 'User Role updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


# ✅ DELETE Role (Hard Delete)
@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def userrole_delete(request, pk):
    if request.method == 'DELETE':
        try:
            userrole = get_object_or_404(UserRole, pk=pk)
            userrole.delete()
            return JsonResponse({'message': 'User Role deleted permanently'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


@csrf_exempt
@authenticate
# # @restrict(roles=['Admin', 'SuperAdmin'])
def userrole_permissions(request, role_name):
    if request.method == 'GET':
        try:
            # Filter by role_name and not deleted
            roles = UserRole.objects.filter(
                role_name=role_name, is_deleted=False)

            if not roles.exists():
                return JsonResponse({'message': 'Role not found or no permissions assigned'}, status=404)

            permissions = []
            for role in roles:
                if role.permission:  # ensure permission exists
                    permissions.append({
                        'permission_name': role.permission.permission_name,
                        'can_create': role.can_create,
                        'can_update': role.can_update,
                        'can_delete': role.can_delete,
                        'can_export': role.can_export
                    })

            # take priority from the first matching row
            role_priority = roles.first().role_priority

            return JsonResponse({
                'role_name': role_name,
                'role_priority': role_priority,
                'permissions': permissions
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def all_roles_with_permissions(request):
    if request.method == 'GET':
        try:

            role_rows = (
                UserRole.objects
                .filter(is_deleted=False)
                .values('role_name')
                .annotate(
                    primary_id=Min('userrole_id'),
                    role_priority=Min('role_priority')  # ✅ add this
                )
                .order_by('role_name')
            )

            all_roles = []
            for row in role_rows:
                role_name = row['role_name']
                primary_id = row['primary_id']
                role_priority = row['role_priority']  # ✅ now exists

                permissions_qs = UserRole.objects.filter(
                    role_name=role_name, is_deleted=False
                )

                permissions = []
                for role in permissions_qs:
                    if role.permission:
                        permissions.append({
                            'permission_id': role.permission_id,
                            'permission_name': role.permission.permission_name,
                            'can_create': role.can_create,
                            'can_update': role.can_update,
                            'can_delete': role.can_delete,
                            'can_export': role.can_export
                        })

                all_roles.append({
                    'id': primary_id,
                    'role_name': role_name,
                    'role_priority': role_priority,   # ✅ added to response
                    'permissions': permissions
                })

            return JsonResponse({'roles': all_roles}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def bulk_update_role_permissions(request):
    print("Request method: ", request.method)
    print("Headers: ", request.headers)
    if request.method in ['PUT', 'POST']:
        print("request method : ", request.method)
        try:
            data = json.loads(request.body)
            role_name = data.get('role_name')
            updates = data.get('updates')

            if not role_name or not updates:
                return JsonResponse({'message': 'Role name and updates are required'}, status=400)

            updated_count = 0

            for item in updates:
                permission_id = item.get('permission_id')
                if permission_id is None:
                    continue

                # Find the UserRole entry for this role and permission
                userrole = UserRole.objects.filter(
                    role_name=role_name,
                    permission_id=permission_id,
                    is_deleted=False
                ).first()

                if userrole:
                    # Update only if keys are provided
                    if 'can_create' in item:
                        userrole.can_create = item['can_create']
                    if 'can_update' in item:
                        userrole.can_update = item['can_update']
                    if 'can_delete' in item:
                        userrole.can_delete = item['can_delete']
                    if 'can_export' in item:
                        userrole.can_export = item['can_export']

                    userrole.updated = timezone.now()
                    userrole.updated_emp_id = request.user.get('emp_id')
                    userrole.updatedby = None
                    userrole.save()
                    updated_count += 1

            return JsonResponse({'message': f'{updated_count} permissions updated successfully'}, status=200)

        except Exception as e:
            print("error : ", e)
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def assign_role_permissions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            role_name = data.get('role_name')
            assignments = data.get('assignments', [])

            if not role_name or not isinstance(assignments, list) or not assignments:
                return JsonResponse({'message': 'role_name and assignments are required'}, status=400)

            changed = 0
            for a in assignments:
                pid = a.get('permission_id')
                if pid is None:
                    continue

                ur, created = UserRole.objects.get_or_create(
                    role_name=role_name,
                    permission_id=pid,
                    defaults={
                        'role_priority': None,
                        'createdby': None, 'updatedby': None,
                        'created_emp_id': request.user.get('emp_id'),
                        'updated_emp_id': request.user.get('emp_id'),
                        'can_create': bool(a.get('can_create')),
                        'can_update': bool(a.get('can_update')),
                        'can_delete': bool(a.get('can_delete')),
                        'can_export': bool(a.get('can_export')),
                    }
                )
                if not created:
                    if 'can_create' in a:
                        ur.can_create = bool(a['can_create'])
                    if 'can_update' in a:
                        ur.can_update = bool(a['can_update'])
                    if 'can_delete' in a:
                        ur.can_delete = bool(a['can_delete'])
                    if 'can_export' in a:
                        ur.can_export = bool(a['can_export'])
                    ur.updated = timezone.now()
                    ur.updated_emp_id = request.user.get('emp_id')
                    ur.updatedby = None
                    ur.save()
                changed += 1

            return JsonResponse({'message': f'{changed} assignment(s) applied'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'message': 'Method Not Allowed'}, status=405)


@csrf_exempt
@authenticate
# @restrict(roles=['Admin', 'SuperAdmin'])
def remove_role_permission(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            role_name = data.get('role_name')
            permission_id = data.get('permission_id')

            if not role_name or not permission_id:
                return JsonResponse({'message': 'role_name and permission_id are required'}, status=400)

            userrole = UserRole.objects.filter(
                role_name=role_name,
                permission_id=permission_id,
                is_deleted=False
            ).first()

            if not userrole:
                return JsonResponse({'message': 'Permission not found for this role'}, status=404)

            userrole.delete()  # hard delete
            return JsonResponse({'message': 'Permission removed successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'message': 'Method Not Allowed'}, status=405)