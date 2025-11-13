# Generated migration for adding material_group field to Request model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0010_request_type'),
        ('matgroups', '0001_initial'),  # Adjust this based on your actual matgroups migration
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='material_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='requests',
                to='matgroups.matgroup'
            ),
        ),
    ]

