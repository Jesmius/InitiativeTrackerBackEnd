from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'characters', views.CharacterViewSet, basename='character')
router.register(r'enemies', views.EnemyViewSet, basename='enemy')
router.register(r'combats', views.CombatViewSet, basename='combat')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('combats/<int:combat_id>/participants/', views.CombatParticipantListView.as_view(), name='combat-participants'),
    path('participants/<int:pk>/', views.CombatParticipantDetailView.as_view(), name='participant-detail'),
    path('party/', views.PartyMemberListView.as_view(), name='party-members'),
    path('party/<int:pk>/', views.PartyMemberDetailView.as_view(), name='party-member-detail'),
    path('', include(router.urls)),
]
