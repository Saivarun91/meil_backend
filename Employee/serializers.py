# in Employees/serializers.py (or a common auth app)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # ✅ add custom claims
        token["emp_id"] = user.emp_id
        token["email"] = user.email
        token["role"] = user.role.role_name if user.role else None

        return token
