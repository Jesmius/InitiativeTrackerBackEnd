from django.contrib import admin
from .models import UserProfile, Character, Enemy, Combat, CombatParticipant


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'player', 'initiative_bonus', 'created_at']
    list_filter = ['player']
    search_fields = ['name', 'player__username']


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_display = ['name', 'master', 'initiative_bonus', 'hp', 'passive_defense']
    list_filter = ['master']
    search_fields = ['name', 'master__username']


class CombatParticipantInline(admin.TabularInline):
    model = CombatParticipant
    extra = 0
    fields = ['character', 'enemy', 'initiative_value', 'order', 'is_alive', 'current_hp']


@admin.register(Combat)
class CombatAdmin(admin.ModelAdmin):
    list_display = ['name', 'master', 'is_active', 'round_number', 'current_turn_index', 'created_at']
    list_filter = ['is_active', 'master']
    search_fields = ['name', 'master__username']
    inlines = [CombatParticipantInline]


@admin.register(CombatParticipant)
class CombatParticipantAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'combat', 'initiative_value', 'order', 'is_alive']
    list_filter = ['is_alive', 'combat']
