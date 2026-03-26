from rest_framework import serializers
from .models import ValidationLists


class ValidationListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationLists
        fields = '__all__'
