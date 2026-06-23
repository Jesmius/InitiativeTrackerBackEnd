from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Initiative Tracker API",
        default_version='v1',
        description=(
            "API para gerenciamento de iniciativa em RPG de mesa.\n\n"
            "**Tipos de usuário:**\n"
            "- `master` — Mestre de Mesa: cria inimigos e combates\n"
            "- `player` — Jogador: vê seus combates e passa o turno\n\n"
            "**Autenticação:** Use `POST /api/auth/token/` para obter o JWT, "
            "depois inclua o header `Authorization: Bearer <token>` nas requisições."
        ),
        contact=openapi.Contact(email=""),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('initiative.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
