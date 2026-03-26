from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itemmaster', '0008_itemmaster_is_final'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemmaster',
            name='uom',
            field=models.CharField(blank=True, help_text='Unit of Measure', max_length=50, null=True),
        ),
    ]
