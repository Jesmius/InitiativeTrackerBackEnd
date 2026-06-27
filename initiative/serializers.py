from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Character, Enemy, Combat, CombatParticipant, PartyMember


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        default=UserProfile.ROLE_PLAYER,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role', UserProfile.ROLE_PLAYER)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, role=role)
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['id', 'username']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'As senhas não coincidem.'})
        return data


class CharacterSerializer(serializers.ModelSerializer):
    player_username = serializers.CharField(source='player.username', read_only=True)

    class Meta:
        model = Character
        fields = ['id', 'name', 'player', 'player_username', 'initiative_bonus', 'created_at', 'updated_at']
        read_only_fields = ['id', 'player', 'created_at', 'updated_at']


class EnemySerializer(serializers.ModelSerializer):
    master_username = serializers.CharField(source='master.username', read_only=True)

    class Meta:
        model = Enemy
        fields = ['id', 'name', 'master', 'master_username', 'initiative_bonus', 'hp', 'passive_defense', 'created_at', 'updated_at']
        read_only_fields = ['id', 'master', 'created_at', 'updated_at']


class CombatParticipantSerializer(serializers.ModelSerializer):
    character_name = serializers.CharField(source='character.name', read_only=True, allow_null=True)
    character_player_id = serializers.IntegerField(source='character.player_id', read_only=True, allow_null=True)
    enemy_name = serializers.CharField(source='enemy.name', read_only=True, allow_null=True)
    display_name = serializers.CharField(read_only=True)
    participant_type = serializers.CharField(read_only=True)

    class Meta:
        model = CombatParticipant
        fields = [
            'id', 'combat', 'character', 'character_name', 'character_player_id',
            'enemy', 'enemy_name', 'display_name', 'participant_type',
            'initiative_value', 'order', 'is_alive', 'current_hp', 'name_override'
        ]
        read_only_fields = ['id', 'combat']

    def validate(self, data):
        if self.partial:
            return data
        character = data.get('character')
        enemy = data.get('enemy')
        if not character and not enemy:
            raise serializers.ValidationError("Um participante deve ser um personagem ou um inimigo.")
        if character and enemy:
            raise serializers.ValidationError("Um participante não pode ser personagem e inimigo ao mesmo tempo.")
        return data


class PartyMemberSerializer(serializers.ModelSerializer):
    player_username = serializers.CharField(source='player.username', read_only=True)
    player_id = serializers.IntegerField(source='player.id', read_only=True)

    class Meta:
        model = PartyMember
        fields = ['id', 'player_id', 'player_username']


class CombatParticipantCreateSerializer(CombatParticipantSerializer):
    class Meta(CombatParticipantSerializer.Meta):
        read_only_fields = ['id', 'combat', 'order']


class CombatSerializer(serializers.ModelSerializer):
    participants = CombatParticipantSerializer(many=True, read_only=True)
    master_username = serializers.CharField(source='master.username', read_only=True)
    current_participant_id = serializers.SerializerMethodField()

    class Meta:
        model = Combat
        fields = [
            'id', 'name', 'master', 'master_username',
            'is_active', 'current_turn_index', 'round_number',
            'current_participant_id', 'created_at', 'updated_at', 'participants'
        ]
        read_only_fields = ['id', 'master', 'current_turn_index', 'round_number', 'created_at', 'updated_at']

    def get_current_participant_id(self, obj):
        current = obj.get_current_participant()
        return current.id if current else None
