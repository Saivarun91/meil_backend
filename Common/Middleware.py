# import jwt
# from django.conf import settings
# from django.http import JsonResponse
# from functools import wraps


# def authenticate(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         auth_header = request.META.get('HTTP_AUTHORIZATION')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return JsonResponse({'message': 'Authorization denied'}, status=401)
#         try:
#             token = auth_header.split(' ')[1]
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#             request.user = {
#                 'emp_id': payload.get('emp_id'),
#                 'emp_name': payload.get('emp_name'),
#                 'role': payload.get('role')
#             }
#             print("Authenticated user:", payload)
#         except jwt.ExpiredSignatureError:
#             return JsonResponse({'message': 'Token expired'}, status=401)
#         except jwt.InvalidTokenError:
#             return JsonResponse({'message': 'Invalid token'}, status=401)
#         return view_func(request, *args, **kwargs)
#     return wrapper

# def restrict(roles=[]):
#     def decorator(view_func):
#         @wraps(view_func)
#         def wrapper(request, *args, **kwargs):
#             user = getattr(request, 'user', None)
#             if not user:
#                 return JsonResponse({'message': "User not authenticated"}, status=401)
#             if user.get('role') not in roles:
#                 return JsonResponse({'message': "You're not authorized"}, status=403)
#             return view_func(request, *args, **kwargs)
#         return wrapper
#     return decorator
# middleware.py
import jwt
from django.conf import settings
from django.http import JsonResponse
from functools import wraps


# 🔹 Authentication Middleware
def authenticate(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"message": "Authorization denied"}, status=401)

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Attach user info to request
            request.user = {
                "user_id": payload.get("user_id"),
                "emp_id": payload.get("emp_id"),
                "email": payload.get("email"),
                "role": payload.get("role"),
            }
            print("[OK] Authenticated user:", request.user)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


# 🔹 Role Restriction Middleware
def restrict(roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None)

            if not user:
                return JsonResponse({"message": "User not authenticated"}, status=401)

            if roles and user.get("role") not in roles:
                return JsonResponse({"message": "You're not authorized"}, status=403)

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator

