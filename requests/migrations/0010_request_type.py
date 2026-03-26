# Generated migration for adding type field to Request model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0009_request_request_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

