from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itemmaster', '0009_itemmaster_uom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemmaster',
            name='sap_item_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
