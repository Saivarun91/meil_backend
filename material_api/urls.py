from django.urls import path
from . import views

urlpatterns = [
    # ==========================================================
    # 🔹 1. Free Text Search (Hybrid BM25 + Trigram)
    # ==========================================================
    path('matgroups/search/', views.search_groups, name='search_groups'),

    # ==========================================================
    # 🔹 2. Drill-Down Search Endpoints
    # ==========================================================
    # Get all top-level super material groups
    path('matgroups/super-groups/', views.super_material_groups, name='super_material_groups'),

    # Get all material groups under a specific super group
    path('matgroups/super-groups/<str:super_code>/material-groups/', 
         views.material_groups_by_super, name='material_groups_by_super'),

    # Get all material types inside a material group (used in drill-down)
    path('matgroups/<str:mgrp_code>/materials/', 
         views.materials_by_matgroup, name='materials_by_matgroup'),

    # Get all items under a material type (used in drill-down)
    path('materials/<str:mat_type_code>/items/', 
         views.items_by_material_type, name='items_by_material_type'),

    # ==========================================================
    # 🔹 3. Direct Search by Material Group Code
    # ==========================================================
    path('matgroups/by-code/<str:mgrp_code>/', 
         views.search_by_matgroup_code, name='search_by_matgroup_code'),

    # ==========================================================
    # 🔹 4. Item Retrieval APIs (existing ones)
    # ==========================================================
    # Get all materials inside a selected group
    path('matgroups/<str:group_code>/materials/', 
         views.materials_by_matgroup, name='materials_by_group'),

    # Get all items inside a selected group
    path('matgroups/<str:group_code>/items/', 
         views.items_by_group, name='items_by_group'),

    # Get SAP IDs for a specific group
    path('matgroups/<str:group_code>/items/sap_ids/', 
         views.sap_ids_by_matgroup, name='sap_ids_by_matgroup'),

    # Get all items by group + material type
    path('matgroups/<str:group_code>/items/<str:mat_type_code>/', 
         views.items_by_group_and_type, name='items_by_group_and_type'),
     
     
    # Get item details with attributes
    path('items/<str:item_id>/details/', 
         views.item_details_with_attributes, name='item_details_with_attributes'),


]
