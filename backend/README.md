# Backend - Copa do Mundo Tech API 🚀🐍

Este diretório contém a API REST do projeto **Alura Album**, construída em Python utilizando o framework **FastAPI**. A API gerencia a persistência das figurinhas no banco de dados SQLite, o cadastro/autenticação de usuários via JWT, e as coleções personalizadas de figurinhas coladas no álbum.

---

## 🛠️ Requisitos e Dependências

- **Python 3.10 ou superior**
- **FastAPI:** Framework para criação de APIs rápidas e assíncronas.
- **Uvicorn:** Servidor ASGI de alto desempenho para rodar o app.
- **PyJWT:** Geração e validação de tokens JWT para segurança.
- **SQLAlchemy 2.0:** Camada de acesso a banco portátil (SQLite para desenvolvimento, PostgreSQL para produção).
- **psycopg (v3):** Driver do PostgreSQL (obrigatório em produção com `DATABASE_URL`).

---

## ⚙️ Configuração do Banco de Dados

O banco é escolhido pela variável de ambiente `DATABASE_URL`:

| Valor de `DATABASE_URL` | Banco utilizado |
|---|---|
| Vazia (padrão) | SQLite local (`backend/album.db`) — criado e semeado automaticamente com as 40 figurinhas |
| `postgresql://usuario:senha@host:5432/nome` | PostgreSQL (Neon, Supabase, Render Postgres, Docker...) — tabelas e seed também automáticos |

Exemplo com Docker (teste rápido):
```bash
docker run -d --name alura-album-db -e POSTGRES_PASSWORD=senha -e POSTGRES_DB=alura_album -p 5432:5432 postgres:16-alpine
```

## 🚀 Passo a Passo de Instalação e Execução

Siga os passos a seguir no terminal para configurar e rodar o backend localmente:

### 1. Criar o Ambiente Virtual (venv)

No diretório do backend, crie um ambiente virtual isolado para as dependências:

```bash
python -m venv .venv
```

### 2. Ativar o Ambiente Virtual

Ative o ambiente virtual conforme o seu sistema operacional:

- **No Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **No Windows (Prompt de Comando - CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **No Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

> [!NOTE]
> Quando ativado, você verá `(.venv)` no início da linha de comandos do terminal.

### 3. Instalar as Dependências

Com a venv ativa, instale as bibliotecas registradas no projeto:

```bash
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente e Segurança (.env)

1. Crie o arquivo `.env` a partir do modelo [.env.example](./.env.example):
   ```bash
   # Windows (PowerShell):  copy .env.example .env
   # Linux / macOS:         cp .env.example .env
   ```
2. Abra o arquivo `.env` gerado e defina uma chave secreta e aleatória na variável `JWT_SECRET_KEY`. Você pode gerar uma chave segura rodando o comando:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. (Opcional) Para usar PostgreSQL em vez do SQLite, adicione a linha `DATABASE_URL=postgresql://usuario:senha@host:5432/nome` no `.env`.

> [!IMPORTANT]
> A variável `JWT_SECRET_KEY` é **obrigatória**: o servidor não inicia sem ela. Isso evita que chaves padrão publicadas acidentalmente no GitHub sejam usadas em produção.

### 5. Executar o Servidor FastAPI

Execute a API em modo de desenvolvimento com o Uvicorn:

```bash
uvicorn main:app --reload
```

- O servidor será iniciado no endereço local: `http://127.0.0.1:8000`
- O banco de dados (SQLite `album.db` ou PostgreSQL) é criado e semeado automaticamente com as 40 figurinhas no primeiro início.

> [!NOTE]
> Os endpoints `POST /auth/register` e `POST /auth/login` possuem **limite de tentativas por IP** (10 por minuto por padrão, configurável via `RATE_LIMIT_MAX_REQUESTS` e `RATE_LIMIT_WINDOW_SECONDS`) para evitar ataques de força bruta.

---

## 🔌 Rotas e Endpoints da API

Abaixo estão listadas as rotas expostas em [main.py](./main.py):

### 🏠 Páginas e Auxiliares

- **`GET /`**: Serve o frontend [index.html](../frontend/index.html) diretamente a partir do backend.
- **`GET /api`**: Roda o diagnóstico de integridade da API (Healthcheck).
- **`/figurinhas_img`**: Servidor de arquivos estáticos local para as imagens de figurinhas colecionáveis em alta resolução.

### 🖼️ Banco de Figurinhas Geral

- **`GET /figurinhas`**: Lista todas as figurinhas registradas. Suporta busca por parâmetros na query `?nome=Alan&categoria=IA`.
- **`GET /figurinhas/{id}`**: Detalhes técnicos e papel histórico de uma figurinha pelo ID.

### 🔑 Autenticação de Usuários

- **`POST /auth/register`**: Cadastra um novo colecionador no SQLite.
- **`POST /auth/login`**: Valida a senha (criptografada) e retorna um Token JWT válido por 24 horas.
- **`GET /auth/me`**: Rota protegida que retorna o perfil do usuário logado. (Requer Header `Authorization: Bearer <TOKEN>`).

### 📦 Coleção do Álbum (Customizado por Usuário)

- **`GET /figurinhas/user/me`**: Lista os IDs de todas as figurinhas coladas pelo usuário autenticado.
- **`POST /figurinhas/user/me/collect/{figurinha_id}`**: Cola a figurinha correspondente ao ID informado na conta do usuário logado.
- **`DELETE /figurinhas/user/me/collect/{figurinha_id}`**: Descola a figurinha correspondente ao ID informado do álbum do usuário logado.

---

## 🧪 Como Testar a API no Swagger UI

O FastAPI gera automaticamente uma página de testes interativa (Swagger UI) que você pode acessar em:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Para testar as rotas protegidas (como `/auth/me` e `/collect`):

1. Expanda a rota **`POST /auth/login`**, clique em **"Try it out"**, insira as credenciais de um usuário e execute.
2. Copie o valor do `access_token` retornado no Response Body (sem aspas).
3. Role até o topo da página, clique no botão verde **"Authorize"** (cadeado).
4. Cole o token copiado no campo **Value** (sem digitar a palavra Bearer) e clique em **Authorize**.
5. Agora você pode testar qualquer rota de coleção e autenticação clicando em **Execute**.

---

## 🛡️ Segurança e GitHub (.gitignore)

> [!WARNING]
> O arquivo `.env` que armazena a chave criptográfica **nunca** deve ser enviado ao GitHub. Ele está devidamente listado no arquivo [.gitignore](../.gitignore).
>
> O arquivo do banco de dados SQLite (`album.db`) também é ignorado no Git para evitar subir dados locais ou cadastros de teste dos usuários para a nuvem.

## 🌐 Deploy no Render

1. No painel do Render, conecte o repositório e configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Configure as variáveis de ambiente no painel:
   - `JWT_SECRET_KEY` (obrigatória — gere uma nova chave e nunca reutilize chaves publicadas no GitHub)
   - `DATABASE_URL` (recomendado — crie um PostgreSQL gratuito no Neon, Supabase ou Render Postgres para os dados persistirem entre deploys)
