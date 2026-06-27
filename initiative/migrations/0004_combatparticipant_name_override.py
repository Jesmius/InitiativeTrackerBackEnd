from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('initiative', '0003_partymember'),
    ]

    operations = [
        migrations.AddField(
            model_name='combatparticipant',
            name='name_override',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
