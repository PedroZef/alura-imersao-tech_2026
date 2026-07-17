import os
import glob
import logging
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Logger do sistema
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("alura-album-api")

import jwt
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from fastapi import Depends, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import (
    init_db,
    get_all_figurinhas,
    get_figurinha_by_id,
    create_user,
    get_user_by_username,
    verify_password,
    get_user_collected_stickers,
    collect_sticker,
    uncollect_sticker
)
from schemas import (
    FigurinhaSchema,
    HealthCheckSchema,
    UserRegisterSchema,
    UserLoginSchema,
    TokenSchema,
    UserResponseSchema
)

# --- CONFIGURAÇÃO DE SEGURANÇA E JWT ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "7b049ad88d9298492026850c9535deabcfad82a93b3f2c5ad2e779a1f2bc837e")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Gera um token JWT com data de expiração."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependência para autenticar requisições usando o token JWT."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: identificador de usuário não encontrado."
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )
        
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário associado ao token não existe mais."
        )
    return user

# --- CONFIGURAÇÃO DE DIRETÓRIOS E CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Direretório 'backend'
ROOT_DIR = os.path.dirname(BASE_DIR)                  # Direretório raiz do projeto

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
PASTA_IMAGENS = os.path.join(PASTA_BASE, "imgs")

caminho_imagens = os.path.join(BASE_DIR, "imgs")
caminho_frontend = os.path.join(ROOT_DIR, "frontend")
caminho_src = os.path.join(caminho_frontend, "src")
caminho_index_html = os.path.join(caminho_frontend, "index.html")

# --- LISTA ESTÁTICA DE FIGURINHAS ---
figurinhas = [
    {"id": 1, "nome": "Alan Turing", "categoria": "IA", "imagem_url": "/figurinhas/1/imagem", "papel": "Fundamentos da computação e do conceito de IA"},
    {"id": 2, "nome": "John McCarthy", "categoria": "IA", "imagem_url": "/figurinhas/2/imagem", "papel": "Criou o termo \"Artificial Intelligence\""},
    {"id": 3, "nome": "Sam Altman", "categoria": "IA", "imagem_url": "/figurinhas/3/imagem", "papel": "Co-fundador e CEO da OpenAI"},
    {"id": 4, "nome": "Geoffrey Hinton", "categoria": "IA", "imagem_url": "/figurinhas/4/imagem", "papel": "Deep learning e redes neurais modernas"},
    {"id": 5, "nome": "Yann LeCun", "categoria": "IA", "imagem_url": "/figurinhas/5/imagem", "papel": "Redes convolucionais e visão computacional"},
    {"id": 6, "nome": "Guido van Rossum", "categoria": "Python", "imagem_url": "/figurinhas/6/imagem", "papel": "Criador da linguagem Python"},
    {"id": 7, "nome": "Tim Peters", "categoria": "Python", "imagem_url": "/figurinhas/7/imagem", "papel": "Autor do \"Zen of Python\""},
    {"id": 8, "nome": "Raymond Hettinger", "categoria": "Python", "imagem_url": "/figurinhas/8/imagem", "papel": "Um dos maiores educadores de Python"},
    {"id": 9, "nome": "Travis Oliphant", "categoria": "Python", "imagem_url": "/figurinhas/9/imagem", "papel": "Criador do NumPy"},
    {"id": 10, "nome": "Wes McKinney", "categoria": "Python", "imagem_url": "/figurinhas/10/imagem", "papel": "Criador do pandas"},
    {"id": 11, "nome": "Edgar F. Codd", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/11/imagem", "papel": "Inventor do modelo relacional"},
    {"id": 12, "nome": "Larry Ellison", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/12/imagem", "papel": "Fundador da Oracle Corporation"},
    {"id": 13, "nome": "Michael Widenius", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/13/imagem", "papel": "Criador do MySQL"},
    {"id": 14, "nome": "Salvatore Sanfilippo", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/14/imagem", "papel": "Criador do Redis"},
    {"id": 15, "nome": "Eliot Horowitz", "categoria": "Banco de Dados", "imagem_url": "/figurinhas/15/imagem", "papel": "Cocriador do MongoDB"},
    {"id": 16, "nome": "Linus Torvalds", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas/16/imagem", "papel": "Criador do Linux & Git"},
    {"id": 17, "nome": "Dennis Ritchie", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas/17/imagem", "papel": "Co-criador do Unix & C"},
    {"id": 18, "nome": "Richard Stallman", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas/18/imagem", "papel": "Projeto GNU / Free Software"},
    {"id": 19, "nome": "Bill Gates", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas/19/imagem", "papel": "Co-fundador da Microsoft"},
    {"id": 20, "nome": "Steve Jobs", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas/20/imagem", "papel": "Co-fundador da Apple"},
    {"id": 21, "nome": "Paulo Silveira", "categoria": "Brasil", "imagem_url": "/figurinhas/21/imagem", "papel": "Co-fundador da Alura"},
    {"id": 22, "nome": "Guilherme Silveira", "categoria": "Brasil", "imagem_url": "/figurinhas/22/imagem", "papel": "Co-fundador da Alura"},
    {"id": 23, "nome": "Gustavo Guanabara", "categoria": "Brasil", "imagem_url": "/figurinhas/23/imagem", "papel": "Criador do Curso em Vídeo"},
    {"id": 24, "nome": "Maurício Aniche", "categoria": "Brasil", "imagem_url": "/figurinhas/24/imagem", "papel": "Engenharia de Software / Educador"},
    {"id": 25, "nome": "Andre David", "categoria": "Brasil", "imagem_url": "/figurinhas/25/imagem", "papel": "Coordenador da FIAP"},
    {"id": 26, "nome": "Guilherme Lima", "categoria": "Brasil", "imagem_url": "/figurinhas/26/imagem", "papel": "Alura / Tech Educator"},
    {"id": 27, "nome": "Gi Space Coding", "categoria": "Brasil", "imagem_url": "/figurinhas/27/imagem", "papel": "Giovanna Souza / Creator"},
    {"id": 28, "nome": "Vinicius Neves", "categoria": "Brasil", "imagem_url": "/figurinhas/28/imagem", "papel": "Desenvolvedor FullStack"},
    {"id": 29, "nome": "Rafaela Ballerini", "categoria": "Brasil", "imagem_url": "/figurinhas/29/imagem", "papel": "Alura / Tech Educator"},
    {"id": 30, "nome": "Pedro Zeferino", "categoria": "Brasil", "imagem_url": "/figurinhas/30/imagem", "papel": "Desenvolvedor"},
    {"id": 31, "nome": "James Gosling", "categoria": "Java", "imagem_url": "/figurinhas/31/imagem", "papel": "Criador da linguagem Java"},
    {"id": 32, "nome": "Patrick Naughton", "categoria": "Java", "imagem_url": "/figurinhas/32/imagem", "papel": "Cocriador do Java / Green Project"},
    {"id": 33, "nome": "Mike Sheridan", "categoria": "Java", "imagem_url": "/figurinhas/33/imagem", "papel": "Cocriador do Java / Green Project"},
    {"id": 34, "nome": "Mark Reinhold", "categoria": "Java", "imagem_url": "/figurinhas/34/imagem", "papel": "Arquiteto-chefe da plataforma Java"},
    {"id": 35, "nome": "Brian Goetz", "categoria": "Java", "imagem_url": "/figurinhas/35/imagem", "papel": "Arquiteto de linguagem Java na Oracle"},
    {"id": 36, "nome": "Brendan Eich", "categoria": "JavaScript", "imagem_url": "/figurinhas/36/imagem", "papel": "Criador da linguagem JavaScript"},
    {"id": 37, "nome": "Douglas Crockford", "categoria": "JavaScript", "imagem_url": "/figurinhas/37/imagem", "papel": "Popularizou o JSON e autor influente"},
    {"id": 38, "nome": "Ryan Dahl", "categoria": "JavaScript", "imagem_url": "/figurinhas/38/imagem", "papel": "Criador do runtime Node.js"},
    {"id": 39, "nome": "Anders Hejlsberg", "categoria": "JavaScript", "imagem_url": "/figurinhas/39/imagem", "papel": "Criador do TypeScript e C#"},
    {"id": 40, "nome": "Jordan Walke", "categoria": "JavaScript", "imagem_url": "/figurinhas/40/imagem", "papel": "Criador da biblioteca React"}
]

# --- INICIALIZAÇÃO DO FASTAPI ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o banco de dados SQLite
    try:
        init_db()
        logger.info("Banco de dados SQLite inicializado/verificado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
    yield

app = FastAPI(
    title="Alura Album Tech API",
    description="API para servir o banco de dados de figurinhas e assets estáticos para o projeto Álbum Tech.",
    version="1.2.0",
    lifespan=lifespan
)

# --- CONFIGURAÇÃO DE CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MONTAGEM DE ARQUIVOS ESTÁTICOS ---
# --- ENDPOINT PARA ENTREGAR IMAGENS DAS FIGURINHAS ---
@app.get("/figurinhas_img/{nome_arquivo}")
def obter_imagem_figurinha(nome_arquivo: str):
    """Retorna a imagem de uma figurinha específica por um endpoint próprio."""
    caminho_arquivo = os.path.join(caminho_imagens, nome_arquivo)
    arquivos = glob.glob(caminho_arquivo)
    if not arquivos:
         raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return FileResponse(arquivos[0])


@app.get("/figurinhas/{id}/imagem")
def obter_imagem_figurinha_por_id(id: int):
    """Retorna a imagem de uma figurinha específica pelo ID buscando na pasta de imagens pelo prefixo de 2 dígitos."""
    nome_padrao = f"{id:02d}[!0-9]*"
    caminho_busca = os.path.join(caminho_imagens, nome_padrao)
    arquivos = glob.glob(caminho_busca)
    if not arquivos:
         raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return FileResponse(arquivos[0])

# Servir os arquivos estáticos do frontend (CSS, JS, etc.)
if os.path.exists(caminho_frontend):
    app.mount("/src", StaticFiles(directory=caminho_src), name="src")
    app.mount("/frontend", StaticFiles(directory=caminho_frontend), name="frontend")
    logger.info(f"Frontend montado com sucesso a partir de: {caminho_frontend}")
else:
    logger.warning(f"⚠️ Diretório frontend '{caminho_frontend}' não encontrado.")


# --- ROTAS DE AUTENTICAÇÃO ---

@app.post("/auth/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterSchema) -> dict:
    """Registra um novo usuário no sistema."""
    logger.info(f"Tentativa de registro de usuário: {user_data.username}")
    
    # Verifica se o usuário já existe
    existing_user = get_user_by_username(user_data.username)
    if existing_user:
        logger.warning(f"Tentativa de registro com username já cadastrado: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já está em uso."
        )
        
    new_user = create_user(user_data.username, user_data.password)
    if not new_user:
        logger.error(f"Erro desconhecido ao criar usuário: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível criar o usuário."
        )
        
    logger.info(f"Usuário registrado com sucesso: {user_data.username} (ID: {new_user['id']})")
    return new_user


@app.post("/auth/login", response_model=TokenSchema)
def login(login_data: UserLoginSchema) -> dict:
    """Autentica o usuário e retorna o token JWT."""
    logger.info(f"Tentativa de login: {login_data.username}")
    
    user = get_user_by_username(login_data.username)
    if not user or not verify_password(login_data.password, user["password_hash"]):
        logger.warning(f"Falha de autenticação para: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos."
        )
        
    # Gera o token de acesso
    access_token = create_access_token(data={"sub": user["username"]})
    logger.info(f"Login bem-sucedido: {login_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponseSchema)
def get_me(current_user: dict = Depends(get_current_user)) -> dict:
    """Retorna os dados do usuário autenticado atual."""
    return {"id": current_user["id"], "username": current_user["username"]}


# --- ROTAS DE COLEÇÃO DO ÁLBUM ---

@app.get("/figurinhas/user/me", response_model=List[int])
def listar_figurinhas_usuario(current_user: dict = Depends(get_current_user)) -> List[int]:
    """Retorna os IDs das figurinhas coletadas (coladas) pelo usuário logado."""
    logger.info(f"Listando figurinhas coladas pelo usuário: {current_user['username']}")
    return get_user_collected_stickers(current_user["id"])


@app.post("/figurinhas/user/me/collect/{figurinha_id}")
def colar_figurinha(figurinha_id: int, current_user: dict = Depends(get_current_user)) -> dict:
    """Cola/Adiciona uma figurinha ao álbum do usuário logado."""
    logger.info(f"Usuário {current_user['username']} tentando colar figurinha ID {figurinha_id}")
    
    # Verifica se a figurinha existe no banco de dados
    figurinha = get_figurinha_by_id(figurinha_id)
    if not figurinha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figurinha não encontrada no banco de dados."
        )
        
    sucesso = collect_sticker(current_user["id"], figurinha_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta figurinha já está colada no seu álbum."
        )
        
    logger.info(f"Figurinha ID {figurinha_id} colada com sucesso por {current_user['username']}")
    return {"mensagem": "Figurinha colada com sucesso!", "figurinha_id": figurinha_id}


@app.delete("/figurinhas/user/me/collect/{figurinha_id}")
def descolar_figurinha(figurinha_id: int, current_user: dict = Depends(get_current_user)) -> dict:
    """Remove/Descola uma figurinha do álbum do usuário logado."""
    logger.info(f"Usuário {current_user['username']} tentando descolar figurinha ID {figurinha_id}")
    
    # Verifica se a figurinha existe
    figurinha = get_figurinha_by_id(figurinha_id)
    if not figurinha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figurinha não encontrada no banco de dados."
        )
        
    sucesso = uncollect_sticker(current_user["id"], figurinha_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não possui esta figurinha colada no seu álbum."
        )
        
    logger.info(f"Figurinha ID {figurinha_id} descolada com sucesso por {current_user['username']}")
    return {"mensagem": "Figurinha descolada com sucesso!", "figurinha_id": figurinha_id}


# --- ROTAS DA API ---

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Retorna 204 No Content para silenciar erro 404 de favicon.ico no console do servidor."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/", response_class=FileResponse)
def read_root() -> FileResponse:
    """Serve a página principal do frontend (index.html)."""
    if os.path.exists(caminho_index_html):
        return FileResponse(caminho_index_html)
    logger.error("index.html do frontend não foi encontrado.")
    raise HTTPException(status_code=404, detail="index.html do frontend não foi encontrado.")


@app.get("/api", response_model=HealthCheckSchema)
def hello_world() -> dict:
    """Endpoint simples para verificação de integridade da API (Healthcheck)."""
    return {"mensagem": "Olá, mundo! 🌍", "status": "ok"}


@app.get("/figurinhas", response_model=List[FigurinhaSchema])
def listar_figurinhas(nome: str = None, categoria: str = None) -> list:
    """Retorna a lista completa de figurinhas registradas no álbum, com suporte a busca por nome e categoria."""
    logger.info(f"Requisição para listar figurinhas. Filtros - nome: {nome}, categoria: {categoria}")
    
    # Tratamento para evitar que filtros vazios ou a palavra "string" padrão do Swagger filtrem os resultados
    nome_filtro = None
    if nome and nome.strip() and nome.strip().lower() != "string":
        nome_filtro = nome.strip().lower()
        
    categoria_filtro = None
    if categoria and categoria.strip() and categoria.strip().lower() != "string":
        categoria_filtro = categoria.strip().lower()
        
    res = figurinhas
    if categoria_filtro:
        res = [f for f in res if f["categoria"].lower() == categoria_filtro]
    if nome_filtro:
        res = [f for f in res if nome_filtro in f["nome"].lower()]
        
    return res


@app.get("/figurinhas/{id}", response_model=FigurinhaSchema)
def obter_figurinha(id: int) -> dict:
    """Retorna os detalhes de uma figurinha específica pelo ID único."""
    logger.info(f"Requisição para obter figurinha ID: {id}.")
    figurinha = next((f for f in figurinhas if f["id"] == id), None)
    if figurinha:
        return figurinha
    logger.warning(f"Figurinha com ID {id} não encontrada.")
    raise HTTPException(status_code=404, detail="Figurinha não encontrada.")
