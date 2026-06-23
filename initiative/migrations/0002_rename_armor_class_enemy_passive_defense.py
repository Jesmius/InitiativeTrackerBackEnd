from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('initiative', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enemy',
            old_name='armor_class',
            new_name='passive_defense',
        ),
    ]
