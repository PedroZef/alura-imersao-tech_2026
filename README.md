# Copa do Mundo Tech 🏆💻 - Álbum de Figurinhas Virtual

Este é o repositório principal do projeto **Alura Album - Copa do Mundo Tech**, desenvolvido durante a Imersão Alura (Julho de 2026). O projeto consiste em um Álbum de Figurinhas Virtual interativo que homenageia grandes personalidades da tecnologia nacional e internacional.

O sistema é dividido em um **Frontend** interativo com visual premium e efeitos sonoros, e um **Backend** robusto em Python integrado a um banco de dados relacional.

---

## 🏗️ Arquitetura do Sistema

O projeto segue a arquitetura clássica **Client-Server (Cliente-Servidor)** com separação completa de responsabilidades. O frontend atua como o cliente que consome a API RESTful exposta pelo backend em FastAPI, persistindo os dados em uma base relacional local.

### Diagrama de Fluxo e Componentes

```mermaid
graph TD
    %% Frontend Group
    subgraph Client [Frontend - Cliente]
        UI[Interface HTML5 / CSS3]
        JS[Lógica JS Vanilla / ES6+]
        PF[PageFlip.js - Efeito 3D]
        WA[Web Audio API - Som Procedural]
    end

    %% Backend Group
    subgraph Server [Backend - Servidor FastAPI]
        API[API REST Router]
        JWT[Autenticação JWT / Segurança]
        Static[Static File Server - Servidor de Imagens]
    end

    %% Database Group
    subgraph Database [Banco de Dados Relacional]
        DB[(SQLite - album.db)]
        T_Users[Tabela: users]
        T_Stickers[Tabela: figurinhas]
        T_Collect[Tabela: user_figurinhas]
    end

    %% Interactions
    UI -->|Ações do Usuário| JS
    JS -->|Renderiza Efeitos 3D| PF
    JS -->|Gera Fricção Procedural| WA
    JS -->|Consome Endpoints REST / JWT| API
    API -->|Valida Token| JWT
    API -->|Serve Arquivos de Imagem| Static
    API -->|Queries SQL / ORM| DB
    DB === T_Users
    DB === T_Stickers
    DB === T_Collect
```

---

## 🛠️ Tecnologias e Padrões Modernos Utilizados

### 💻 Frontend (Visual & UX)

- **HTML5 Semântico:** Estrutura clara e acessível para SEO e navegabilidade.
- **CSS3 Moderno (Variações Magenta):** Uso intenso de variáveis customizadas (`:root`), efeitos de reflexo de lombada física, glassmorphism nos modais e animações customizadas (`keyframes`).
- **JavaScript ES6+:** Programação assíncrona baseada em `async/await` e manipulação direta da DOM para atualizações parciais eficientes sem reload da página.
- **Web Audio API:** Síntese procedural de som direto no cliente, garantindo leveza (sem carregar arquivos pesados de áudio) e fidelidade física ao simular a virada das folhas.

### 🐍 Backend (API & Dados)

- **FastAPI:** Um dos frameworks mais modernos do ecossistema Python. Utiliza tipagem de dados nativa (`Pydantic`) para autovalidação de requisições, segurança rápida e geração automatizada de documentação OpenAPI/Swagger.
- **SQLAlchemy 2.0:** ORM/Core de banco de dados portátil entre **SQLite** (desenvolvimento) e **PostgreSQL** (produção), controlado pela variável `DATABASE_URL`.
- **JWT (JSON Web Token):** Padrão de mercado para autenticação stateless (sem sessão pesada no servidor). O token carrega a assinatura digital do usuário criptografada garantindo a integridade.
- **Segurança de Senhas:** Hashes seguros gerados com o algoritmo PBKDF2 e SHA-256 combinados com `salt` aleatório, impedindo ataques de tabelas arco-íris (rainbow tables).
- **Rate Limiting:** Limite de tentativas por IP nos endpoints de login/registro (configurável via variáveis de ambiente), protegendo contra força bruta.

---

## 🚀 Como Executar o Projeto Completo

Para rodar a aplicação integrada, siga estes passos simplificados:

### Passo 1: Executar o Backend

O backend serve a API, o banco de dados e hospeda as páginas estáticas.

1. Navegue até a pasta do backend:
   ```bash
   cd backend
   ```
2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):  .venv\Scripts\Activate.ps1
   # Linux / macOS:         source .venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Crie o arquivo de ambiente com a chave JWT (obrigatória):
   ```bash
   # Windows (PowerShell):  copy .env.example .env
   # Linux / macOS:         cp .env.example .env
   ```
   Abra o `.env` e preencha `JWT_SECRET_KEY` com uma chave segura:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   > ⚠️ Sem a `JWT_SECRET_KEY`, o servidor **não inicia** (proteção contra chaves padrão publicadas no GitHub).

5. Inicie o servidor:
   ```bash
   uvicorn main:app --reload
   ```

### Passo 2: Acessar a Aplicação

Com o backend ativo na porta `8000`, o frontend é servido automaticamente na mesma origem:
👉 Acesse no navegador: **[http://localhost:8000/](http://localhost:8000/)**
👉 Documentação interativa da API (Swagger): **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 💾 Banco de Dados (SQLite ou PostgreSQL)

| Ambiente | Configuração |
|---|---|
| **Desenvolvimento (padrão)** | Sem `DATABASE_URL`: usa o SQLite local (`backend/album.db`), criado e semeado automaticamente com as 40 figurinhas. |
| **Produção (Recomendado)** | Defina `DATABASE_URL` com um PostgreSQL (Neon, Supabase, Render Postgres, etc.): `postgresql://usuario:senha@host:5432/nome_do_banco`. As tabelas e a semeadura acontecem automaticamente no primeiro boot. |

### 🔐 Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `JWT_SECRET_KEY` | ✅ Sim | Chave de assinatura dos tokens JWT. **Nunca** publique no GitHub. |
| `DATABASE_URL` | ❌ Não | URL do PostgreSQL. Se vazia, usa SQLite local. |
| `CORS_ORIGINS` | ❌ Não | Origens permitidas (separadas por vírgula). Padrão: `http://localhost:8000,http://127.0.0.1:8000`. |
| `RATE_LIMIT_MAX_REQUESTS` | ❌ Não | Máximo de tentativas de login/registro por IP (padrão: `10`). |
| `RATE_LIMIT_WINDOW_SECONDS` | ❌ Não | Janela de tempo do limite em segundos (padrão: `60`). |

---

## 🔮 Possíveis Melhorias e Roadmap do Projeto

Embora o sistema atual esteja completo, ele foi projetado de forma modular para permitir futuras evoluções. Seguem algumas sugestões de melhorias arquiteturais e de produto:

### 1. 📦 Mecânica de Pacotinhos e Gamificação

- **Melhoria:** Adicionar uma rota para "abrir pacotinhos" de figurinhas diárias.
- **Impacto:** O usuário não teria todas as figurinhas disponíveis de início. Ele abriria pacotes aleatórios e as figurinhas repetidas poderiam ir para uma área de "repetidas", simulando a experiência real de colecionador.

### 2. 🤝 Sistema de Trocas (WebSockets)

- **Melhoria:** Integrar `FastAPI WebSockets` para permitir que usuários online no álbum façam troca de figurinhas repetidas em tempo real.
- **Impacto:** Criação de uma comunidade ativa e interativa em torno do álbum.

### 3. 🌐 Banco de Dados na Nuvem (PostgreSQL) ✅ Implementado

- **Melhoria:** Substituir o SQLite por uma instância PostgreSQL (hospedada em serviços como RDS, Supabase ou Neon).
- **Impacto:** Permite escalabilidade horizontal da API e garante persistência centralizada para múltiplos usuários concorrentes em produção.
- **Status:** O projeto já suporta PostgreSQL de forma transparente — basta definir `DATABASE_URL` no ambiente (ver tabela de variáveis acima). **Recomendado para o deploy no Render**, pois o filesystem do free tier é efêmero (contas e coleções se perdem a cada deploy/restart com SQLite).

### 4. 🗃️ Armazenamento de Mídia Externo (AWS S3 / Cloudflare R2)

- **Melhoria:** Salvar e servir as imagens das figurinhas a partir de um Bucket compatível com S3 em vez do disco local do backend.
- **Impacto:** Reduz o tamanho do pacote da aplicação, acelera a entrega de imagens via CDN global e reduz a carga no servidor principal de API.

### 5. 🏗️ Migração para Frameworks de Componentes (React / Next.js / Vue)

- **Melhoria:** Reescrever o frontend utilizando Next.js ou React.
- **Impacto:** Melhora o gerenciamento de estado do álbum (o login, a coleção de coladas, as repetições e o PageFlip funcionariam com controle reativo de estados de forma muito mais simples e robusta).

## 🌐 Deploy no Render

- 🔗 [Acesse o Frontend do Álbum Tech ao vivo](https://alura-imersao-tech-2026.onrender.com/)
- ⚙️ [Acesse a API Backend no Render](https://alura-imersao-tech-2026-back.onrender.com)

### Configurando o deploy no Render (após as correções de segurança)

1. **Build Command:** `pip install -r backend/requirements.txt`
2. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT` (diretório de trabalho: `backend`)
3. **Variáveis de Ambiente obrigatórias no painel (Dashboard → Service → Environment):**
   - `JWT_SECRET_KEY`: gere uma chave segura com `python -c "import secrets; print(secrets.token_hex(32))"` e cole no painel. **Nunca** use a chave antiga publicada no GitHub.
   - `DATABASE_URL`: crie um banco gratuito (Neon, Supabase ou Render Postgres) e cole a URL de conexão. Com isso, contas e coleções **persistem** entre deploys.
4. **Recomendado:** habilite `RATE_LIMIT_MAX_REQUESTS`/`RATE_LIMIT_WINDOW_SECONDS` se quiser ajustar a proteção de força bruta.
