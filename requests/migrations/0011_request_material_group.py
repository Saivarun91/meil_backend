# Generated migration for adding material_group field to Request model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0010_request_type'),
        # Note: MatGroup model should already exist, so no explicit dependency needed
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='material_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='request_material_groups',
                to='matgroups.matgroup',
                to_field='mgrp_code'
            ),
        ),
    ]

