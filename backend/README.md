# Backend - Copa do Mundo Tech API 🚀🐍

Este diretório contém a API REST do projeto **Alura Album**, construída em Python utilizando o framework **FastAPI**. A API gerencia a persistência das figurinhas no banco de dados SQLite, o cadastro/autenticação de usuários via JWT, e as coleções personalizadas de figurinhas coladas no álbum.

---

## 🛠️ Requisitos e Dependências

- **Python 3.10 ou superior**
- **FastAPI:** Framework para criação de APIs rápidas e assíncronas.
- **Uvicorn:** Servidor ASGI de alto desempenho para rodar o app.
- **PyJWT:** Geração e validação de tokens JWT para segurança.
- **SQLite3:** Banco de dados relacional em arquivo local (nativo do Python).

---

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

1. Crie uma cópia do arquivo de modelo [.env.example](./.env.example) e renomeie-a para `.env`:
    ```bash
    copy .env.example .env
    ```
2. Abra o arquivo `.env` gerado e defina uma chave secreta e aleatória para a assinatura dos tokens JWT na variável `JWT_SECRET_KEY`. Você pode gerar uma chave segura rodando o comando:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

### 5. Executar o Servidor FastAPI

Execute a API em modo de desenvolvimento com o Uvicorn:

```bash
uvicorn main:app --reload
```

- O servidor será iniciado no endereço local: `http://127.0.0.1:8000`
- O banco de dados SQLite `album.db` será criado e semeado automaticamente com as 40 figurinhas no primeiro início.

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
