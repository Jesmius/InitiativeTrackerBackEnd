from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, Character, Enemy, Combat, CombatParticipant, PartyMember
from .permissions import IsMaster, IsPlayer
from .serializers import (
    RegisterSerializer, UserSerializer, ChangePasswordSerializer, ForgotPasswordSerializer,
    CharacterSerializer, EnemySerializer,
    CombatSerializer, CombatParticipantSerializer, CombatParticipantCreateSerializer,
    PartyMemberSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
        except User.DoesNotExist:
            return Response(
                {'detail': 'Não encontramos uma conta com esse username e email.'},
                status=status.HTTP_404_NOT_FOUND
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Senha redefinida com sucesso.'})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Senha atual incorreta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Senha alterada com sucesso.'})


class CharacterViewSet(viewsets.ModelViewSet):
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_master():
            player_ids = PartyMember.objects.filter(gm=user).values_list('player', flat=True)
            return Character.objects.filter(player__in=player_ids)
        return Character.objects.filter(player=user)

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_master():
            raise PermissionDenied("Mestres não podem criar personagens. Use inimigos.")
        serializer.save(player=user)

    def perform_update(self, serializer):
        character = self.get_object()
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_player() and character.player != user:
            raise PermissionDenied("Você só pode editar seus próprios personagens.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_player() and instance.player != user:
            raise PermissionDenied("Você só pode excluir seus próprios personagens.")
        instance.delete()


class EnemyViewSet(viewsets.ModelViewSet):
    serializer_class = EnemySerializer
    permission_classes = [IsAuthenticated, IsMaster]

    def get_queryset(self):
        return Enemy.objects.filter(master=self.request.user)

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)


class CombatViewSet(viewsets.ModelViewSet):
    serializer_class = CombatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_master():
            return Combat.objects.filter(master=user)
        character_ids = user.characters.values_list('id', flat=True)
        return Combat.objects.filter(
            participants__character__in=character_ids
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'profile') or not user.profile.is_master():
            raise PermissionDenied("Apenas Mestres de Mesa podem criar combates.")
        serializer.save(master=user)

    def perform_update(self, serializer):
        combat = self.get_object()
        if combat.master != self.request.user:
            raise PermissionDenied("Apenas o mestre dono do combate pode editá-lo.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.master != self.request.user:
            raise PermissionDenied("Apenas o mestre dono do combate pode excluí-lo.")
        instance.delete()

    @action(detail=True, methods=['post'], url_path='sort-initiative')
    def sort_initiative(self, request, pk=None):
        combat = self.get_object()
        if combat.master != request.user:
            raise PermissionDenied("Apenas o mestre dono do combate pode reorganizar a iniciativa.")
        participants = list(combat.participants.order_by('-initiative_value'))
        for i, p in enumerate(participants):
            p.order = i
        CombatParticipant.objects.bulk_update(participants, ['order'])
        combat.current_turn_index = 0
        combat.save()
        return Response(self.get_serializer(combat).data)

    @action(detail=True, methods=['post'], url_path='next-turn')
    def next_turn(self, request, pk=None):
        combat = self.get_object()
        user = request.user

        is_master = hasattr(user, 'profile') and user.profile.is_master()

        if not is_master:
            current = combat.get_current_participant()
            if current is None:
                return Response(
                    {'detail': 'Nenhum participante ativo no combate.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if current.character is None or current.character.player != user:
                return Response(
                    {'detail': 'Não é a sua vez.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        combat.advance_turn()
        serializer = self.get_serializer(combat)
        return Response(serializer.data)


class CombatParticipantListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CombatParticipantCreateSerializer
        return CombatParticipantSerializer

    def get_combat(self):
        try:
            combat = Combat.objects.get(pk=self.kwargs['combat_id'])
        except Combat.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Combate não encontrado.")
        return combat

    def get_queryset(self):
        return CombatParticipant.objects.filter(combat_id=self.kwargs['combat_id'])

    def check_combat_access(self, combat):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_master():
            if combat.master != user:
                raise PermissionDenied("Você não é o mestre deste combate.")
        else:
            character_ids = user.characters.values_list('id', flat=True)
            if not combat.participants.filter(character__in=character_ids).exists():
                raise PermissionDenied("Você não participa deste combate.")

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'profile') or not user.profile.is_master():
            raise PermissionDenied("Apenas Mestres de Mesa podem adicionar participantes.")
        combat = self.get_combat()
        if combat.master != user:
            raise PermissionDenied("Você não é o mestre deste combate.")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        combat = self.get_combat()
        next_order = CombatParticipant.objects.filter(combat=combat).count()
        participant = serializer.save(combat=combat, order=next_order)
        if participant.enemy and participant.current_hp is None:
            participant.current_hp = participant.enemy.hp
            participant.save()

    def list(self, request, *args, **kwargs):
        combat = self.get_combat()
        self.check_combat_access(combat)
        return super().list(request, *args, **kwargs)


class CombatParticipantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CombatParticipantSerializer
    permission_classes = [IsAuthenticated]
    queryset = CombatParticipant.objects.all()

    def update(self, request, *args, **kwargs):
        participant = self.get_object()
        user = request.user
        is_master = hasattr(user, 'profile') and user.profile.is_master()

        if not is_master:
            if not (participant.character and participant.character.player == user):
                raise PermissionDenied("Você não tem permissão para editar este participante.")
            current_hp_raw = request.data.get('current_hp')
            if current_hp_raw is None:
                raise PermissionDenied("Jogadores só podem atualizar o HP de seus personagens.")
            hp = max(0, int(current_hp_raw))
            participant.current_hp = hp
            participant.is_alive = hp > 0
            participant.save()
            serializer = self.get_serializer(participant)
            return Response(serializer.data)

        if participant.combat.master != user:
            raise PermissionDenied("Você não é o mestre deste combate.")
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user
        if not hasattr(user, 'profile') or not user.profile.is_master():
            raise PermissionDenied("Apenas mestres podem remover participantes.")
        if instance.combat.master != user:
            raise PermissionDenied("Você não é o mestre deste combate.")
        instance.delete()


class PartyMemberListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMaster]
    serializer_class = PartyMemberSerializer

    def get_queryset(self):
        return PartyMember.objects.filter(gm=self.request.user).select_related('player')

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '').strip()
        if not username:
            return Response({'detail': 'Username é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            player = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Jogador não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(player, 'profile') or player.profile.role != UserProfile.ROLE_PLAYER:
            return Response({'detail': 'Esse usuário não é um Jogador.'}, status=status.HTTP_400_BAD_REQUEST)
        member, created = PartyMember.objects.get_or_create(gm=request.user, player=player)
        if not created:
            return Response({'detail': 'Jogador já está na sua lista.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PartyMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PartyMemberDetailView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMaster]
    queryset = PartyMember.objects.all()

    def perform_destroy(self, instance):
        if instance.gm != self.request.user:
            raise PermissionDenied("Você não pode remover jogadores de outra campanha.")
        instance.delete()
