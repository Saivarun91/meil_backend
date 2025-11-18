from rest_framework import serializers
from matgroups.models import MatGroup
from MaterialType.models import MaterialType
from itemmaster.models import ItemMaster


class MatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatGroup
        fields = ["mgrp_code", "mgrp_shortname", "mgrp_longname", "search_type", "notes"]


class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ["mat_type_code", "mat_type_desc"]


class ItemMasterSerializer(serializers.ModelSerializer):
    # Add computed fields for backward compatibility
    item_desc = serializers.CharField(source='short_name', read_only=True)
    notes = serializers.CharField(source='long_name', read_only=True)
    
    class Meta:
        model = ItemMaster
        fields = [
            "local_item_id",
            "sap_item_id",
            "sap_name",
            "item_desc",  # Mapped from short_name for frontend compatibility
            "short_name",
            "notes",  # Mapped from long_name for frontend compatibility
            "long_name",
            "search_text",
            "mat_type_code",
            "mgrp_code",
            "mgrp_long_name",
            "attributes",
            "is_final",
        ]
