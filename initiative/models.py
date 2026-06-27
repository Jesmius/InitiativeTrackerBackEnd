from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_MASTER = 'master'
    ROLE_PLAYER = 'player'
    ROLE_CHOICES = [
        (ROLE_MASTER, 'Mestre de Mesa'),
        (ROLE_PLAYER, 'Jogador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_PLAYER)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_master(self):
        return self.role == self.ROLE_MASTER

    def is_player(self):
        return self.role == self.ROLE_PLAYER


class PartyMember(models.Model):
    gm = models.ForeignKey(User, on_delete=models.CASCADE, related_name='party_members')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gm_memberships')

    class Meta:
        unique_together = [('gm', 'player')]

    def __str__(self):
        return f"{self.player.username} na campanha de {self.gm.username}"


class Character(models.Model):
    name = models.CharField(max_length=100)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    initiative_bonus = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (jogador: {self.player.username})"


class Enemy(models.Model):
    name = models.CharField(max_length=100)
    master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enemies')
    initiative_bonus = models.IntegerField(default=0)
    hp = models.IntegerField(default=1)
    passive_defense = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Inimigo'
        verbose_name_plural = 'Inimigos'

    def __str__(self):
        return f"{self.name} (mestre: {self.master.username})"


class Combat(models.Model):
    name = models.CharField(max_length=100)
    master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='combats')
    is_active = models.BooleanField(default=True)
    current_turn_index = models.IntegerField(default=0)
    round_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Combate'
        verbose_name_plural = 'Combates'

    def __str__(self):
        return f"{self.name} (mestre: {self.master.username})"

    def get_active_participants(self):
        return self.participants.filter(is_alive=True).order_by('order')

    def advance_turn(self):
        active = list(self.get_active_participants())
        if not active:
            return
        next_index = self.current_turn_index + 1
        if next_index >= len(active):
            next_index = 0
            self.round_number += 1
        self.current_turn_index = next_index
        self.save()

    def get_current_participant(self):
        active = list(self.get_active_participants())
        if not active:
            return None
        index = self.current_turn_index % len(active)
        return active[index]


class CombatParticipant(models.Model):
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE, related_name='participants')
    character = models.ForeignKey(
        Character, null=True, blank=True, on_delete=models.SET_NULL, related_name='combat_entries'
    )
    enemy = models.ForeignKey(
        Enemy, null=True, blank=True, on_delete=models.SET_NULL, related_name='combat_entries'
    )
    initiative_value = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    is_alive = models.BooleanField(default=True)
    current_hp = models.IntegerField(null=True, blank=True)
    name_override = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['order']
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'

    def __str__(self):
        name = self.character.name if self.character else (self.enemy.name if self.enemy else '?')
        return f"{name} em '{self.combat.name}' (ordem: {self.order})"

    @property
    def display_name(self):
        if self.name_override:
            return self.name_override
        if self.character:
            return self.character.name
        if self.enemy:
            return self.enemy.name
        return 'Desconhecido'

    @property
    def participant_type(self):
        return 'character' if self.character else 'enemy'
