from rest_framework import serializers
from matgroups.models import MatGroup
from MaterialType.models import MaterialType
from itemmaster.models import ItemMaster


class MatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatGroup
        fields = ["mgrp_code","notes"]


class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ["mat_type_code", "mat_type_desc"]


class ItemMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemMaster
        fields = [
            "local_item_id",
            "sap_item_id",
            "item_desc",
            "notes",
            "search_text",
            "mat_type_code",
            "mgrp_code",
            "attributes",
        ]
