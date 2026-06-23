# Initiative Tracker — Backend

API REST para gerenciamento de iniciativa em RPG de mesa, desenvolvida com Django e Django REST Framework.

## Integrantes

# Lucas Fernandes Alvarenga
# Matrícula: 2210601

## Tecnologias

- Python 3.11+
- Django 4.2
- Django REST Framework 3.17
- SimpleJWT (autenticação JWT)
- drf-yasg (Swagger/OpenAPI)
- django-cors-headers (CORS)

## Instalação local

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repositório>
cd initiative-backend

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 5. Aplique as migrações
python manage.py migrate

# 6. (Opcional) Crie um superusuário para o admin
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`.

## Documentação da API

Com o servidor rodando, acesse:

- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`
- **Admin Django:** `http://localhost:8000/admin/`

## Endpoints principais

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/register/` | Cadastrar usuário | Não |
| POST | `/api/auth/token/` | Login (obter JWT) | Não |
| POST | `/api/auth/token/refresh/` | Renovar token | Não |
| GET/PUT | `/api/auth/profile/` | Ver/editar perfil | Sim |
| POST | `/api/auth/change-password/` | Trocar senha | Sim |
| GET/POST | `/api/characters/` | Listar/criar personagens | Sim |
| GET/PUT/DELETE | `/api/characters/{id}/` | Detalhe do personagem | Sim |
| GET/POST | `/api/enemies/` | Listar/criar inimigos | Mestre |
| GET/PUT/DELETE | `/api/enemies/{id}/` | Detalhe do inimigo | Mestre |
| GET/POST | `/api/combats/` | Listar/criar combates | Sim |
| GET/PUT/DELETE | `/api/combats/{id}/` | Detalhe do combate | Sim |
| POST | `/api/combats/{id}/next-turn/` | Avançar turno | Sim |
| GET/POST | `/api/combats/{id}/participants/` | Participantes | Sim |
| GET/PUT/DELETE | `/api/participants/{id}/` | Detalhe do participante | Mestre |

## Tipos de usuário

- **master** — Mestre de Mesa: cria inimigos, cria combates, adiciona participantes
- **player** — Jogador: vê seus combates, passa o turno quando é sua vez

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | dev key |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Origins do frontend | `http://localhost:5500` |
