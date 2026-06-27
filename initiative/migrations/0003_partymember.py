from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('initiative', '0002_rename_armor_class_enemy_passive_defense'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartyMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='party_members', to=settings.AUTH_USER_MODEL)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gm_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('gm', 'player')},
            },
        ),
    ]
