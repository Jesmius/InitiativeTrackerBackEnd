# Initiative Tracker — Backend

API REST para gerenciamento de iniciativa em sessões de RPG de mesa, desenvolvida com Django e Django REST Framework.

## Integrantes

- Lucas Fernandes Alvarenga — Matrícula: 2210601

## Link do site

- **API ao vivo:** https://initiativetracker.pythonanywhere.com
- **Swagger UI:** https://initiativetracker.pythonanywhere.com/swagger/
- **ReDoc:** https://initiativetracker.pythonanywhere.com/redoc/



## Descrição do projeto

O Initiative Tracker é um sistema para auxiliar sessões de RPG de mesa. O backend expõe uma API REST que gerencia dois tipos de usuários:

- **Mestre de Mesa:** cria e gerencia inimigos, cria combates, adiciona participantes (personagens de jogadores e inimigos) e controla a ordem de turnos.
- **Jogador:** cadastra seus personagens, visualiza os combates em que participa e passa o turno quando chega a sua vez.

O sistema implementa autenticação via JWT e controle de acesso baseado em papéis, garantindo que cada usuário veja e altere apenas os dados que lhe pertencem.

## Tecnologias

- Python 3.11
- Django 4.2
- Django REST Framework 3.17
- djangorestframework-simplejwt (autenticação JWT)
- drf-yasg (Swagger / OpenAPI)
- django-cors-headers (CORS)
- python-decouple (variáveis de ambiente)
- SQLite (banco de dados)

## Instalação local

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repositório>
cd InitiativeTrackerBackEnd

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
# Crie um arquivo .env na raiz do projeto com o conteúdo abaixo:
# SECRET_KEY=sua-chave-secreta-aqui
# DEBUG=True
# ALLOWED_HOSTS=localhost,127.0.0.1
# CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

# 5. Aplique as migrações
python manage.py migrate

# 6. (Opcional) Crie um superusuário para o admin
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`.  
A documentação Swagger estará em `http://localhost:8000/swagger/`.

## Documentação da API

Com o servidor rodando, acesse:

- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`
- **Admin Django:** `http://localhost:8000/admin/`

## Endpoints principais

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/register/` | Cadastrar usuário | Não |
| POST | `/api/auth/forgot-password/` | Redefinir senha | Não |
| POST | `/api/auth/token/` | Login (obter JWT) | Não |
| POST | `/api/auth/token/refresh/` | Renovar token | Não |
| GET/PUT | `/api/auth/profile/` | Ver/editar perfil | Sim |
| POST | `/api/auth/change-password/` | Trocar senha | Sim |
| GET/POST | `/api/characters/` | Listar/criar personagens | Sim |
| GET/PUT/DELETE | `/api/characters/{id}/` | Detalhe do personagem | Sim |
| GET/POST | `/api/enemies/` | Listar/criar inimigos | Mestre |
| GET/PUT/DELETE | `/api/enemies/{id}/` | Detalhe do inimigo | Mestre |
| GET/POST | `/api/party/` | Listar/adicionar jogadores à campanha | Mestre |
| DELETE | `/api/party/{id}/` | Remover jogador da campanha | Mestre |
| GET/POST | `/api/combats/` | Listar/criar combates | Sim |
| GET/PUT/DELETE | `/api/combats/{id}/` | Detalhe do combate | Sim |
| POST | `/api/combats/{id}/next-turn/` | Avançar turno | Sim |
| POST | `/api/combats/{id}/sort-initiative/` | Ordenar por iniciativa | Mestre |
| GET/POST | `/api/combats/{id}/participants/` | Listar/adicionar participantes | Sim |
| PATCH/DELETE | `/api/participants/{id}/` | Editar/remover participante | Mestre / Jogador (só HP) |

## Tipos de usuário

- **master** — Mestre de Mesa: cria inimigos, gerencia a lista de jogadores da campanha, cria combates, adiciona participantes, controla turnos e HP de todos.
- **player** — Jogador: cadastra personagens, visualiza combates em que participa, passa o turno quando é sua vez e atualiza o próprio HP.

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | dev key insegura |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Origins permitidas para CORS | `http://localhost:5500` |

## O que funcionou

- Cadastro e autenticação de usuários com papéis distintos (Mestre e Jogador)
- CRUD completo de personagens, inimigos, combates e participantes
- Sistema de turnos: avanço automático, ordenação por iniciativa, controle de quem pode passar o turno
- Gerência de HP: mestre atualiza HP de todos; jogadores atualizam apenas o próprio HP
- Participantes mortos são ignorados na ordem de turnos
- Sistema de campanha: mestre adiciona jogadores à sua lista; apenas personagens desses jogadores aparecem nos combates
- Documentação completa via Swagger e ReDoc
- Refresh automático de tokens JWT
- Deploy funcional no PythonAnywhere

## O que não funcionou

- A funcionalidade de "esqueci minha senha" não envia email real: o sistema apenas verifica se o username e email coincidem e redefine a senha diretamente. Uma integração com SMTP exigiria configuração adicional de servidor de email.
- O endpoint `/api/participants/{id}/` não aparece corretamente categorizado no Swagger por ser uma view genérica fora do router, o que limita a visualização na interface gráfica.
