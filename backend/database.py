import os
import hashlib
import logging

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger("alura-album-api")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album.db")

# DATABASE_URL pode apontar para um PostgreSQL (ex.: postgresql://usuario:senha@host:5432/nome)
# ou ficar vazio para usar o SQLite local (backend/album.db), ideal para desenvolvimento.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip() or f"sqlite:///{DB_PATH}"

# Garante o uso do driver psycopg 3 (instalado via requirements.txt) com o SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

metadata = MetaData()

figurinhas = Table(
    "figurinhas",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nome", String, nullable=False),
    Column("categoria", String, nullable=False),
    Column("imagem_url", String, nullable=False),
    Column("papel", String, nullable=False),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
)

user_figurinhas = Table(
    "user_figurinhas",
    metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("figurinha_id", ForeignKey("figurinhas.id", ondelete="CASCADE"), primary_key=True),
)

# List of initial stickers for seeding
INITIAL_FIGURINHAS = [
    {"id": 1, "nome": "Alan Turing", "categoria": "IA", "imagem_url": "/figurinhas_img/01-alan-turing.jpg", "papel": "Fundamentos da computação e do conceito de IA"},
    {"id": 2, "nome": "John McCarthy", "categoria": "IA", "imagem_url": "/figurinhas_img/02-john-mccarthy.jpg", "papel": "Criou o termo \"Artificial Intelligence\""},
    {"id": 3, "nome": "Sam Altman", "categoria": "IA", "imagem_url": "/figurinhas_img/03-sam.jpg", "papel": "Co-fundador e CEO da OpenAI"},
    {"id": 4, "nome": "Geoffrey Hinton", "categoria": "IA", "imagem_url": "/figurinhas_img/04-Geoffrey.jpg", "papel": "Deep learning e redes neurais modernas"},
    {"id": 5, "nome": "Yann LeCun", "categoria": "IA", "imagem_url": "/figurinhas_img/05-Yann.jpeg", "papel": "Redes convolucionais e visão computacional"},
    {"id": 6, "nome": "Guido van Rossum", "categoria": "Python", "imagem_url": "/figurinhas_img/06-Guido.jpg", "papel": "Criador da linguagem Python"},
    {"id": 7, "nome": "Tim Peters", "categoria": "Python", "imagem_url": "/figurinhas_img/07-Tim.jpeg", "papel": "Autor do \"Zen of Python\""},
    {"id": 8, "nome": "Raymond Hettinger", "categoria": "Python", "imagem_url": "/figurinhas_img/08-Ray.jpeg", "papel": "Um dos maiores educadores de Python"},
    {"id": 9, "nome": "Travis Oliphant", "categoria": "Python", "imagem_url": "/figurinhas_img/09-Travis.jpg", "papel": "Criador do NumPy"},
    {"id": 10, "nome": "Wes McKinney", "categoria": "Python", "imagem_url": "/figurinhas_img/10-Wes.jpg", "papel": "Criador do pandas"},
    {"id": 11, "nome": "Edgar F. Codd", "categoria": "Banco de Dados", "imagem_url": "/figurinhas_img/11-Edgar.jpeg", "papel": "Inventor do modelo relacional"},
    {"id": 12, "nome": "Larry Ellison", "categoria": "Banco de Dados", "imagem_url": "/figurinhas_img/12-Larry.jpg", "papel": "Fundador da Oracle Corporation"},
    {"id": 13, "nome": "Michael Widenius", "categoria": "Banco de Dados", "imagem_url": "/figurinhas_img/13-Michael.webp", "papel": "Criador do MySQL"},
    {"id": 14, "nome": "Salvatore Sanfilippo", "categoria": "Banco de Dados", "imagem_url": "/figurinhas_img/14-Salvatore.png", "papel": "Criador do Redis"},
    {"id": 15, "nome": "Eliot Horowitz", "categoria": "Banco de Dados", "imagem_url": "/figurinhas_img/15-Eliot.png", "papel": "Cocriador do MongoDB"},
    {"id": 16, "nome": "Linus Torvalds", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas_img/16-Linus.jpg", "papel": "Criador do Linux & Git"},
    {"id": 17, "nome": "Dennis Ritchie", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas_img/17-Dennis.png", "papel": "Co-criador do Unix & C"},
    {"id": 18, "nome": "Richard Stallman", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas_img/18-Richard.jpg", "papel": "Projeto GNU / Free Software"},
    {"id": 19, "nome": "Bill Gates", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas_img/19-bill.jpg", "papel": "Co-fundador da Microsoft"},
    {"id": 20, "nome": "Steve Jobs", "categoria": "Sist. Operacionais", "imagem_url": "/figurinhas_img/20-Steve.webp", "papel": "Co-fundador da Apple"},
    {"id": 21, "nome": "Paulo Silveira", "categoria": "Brasil", "imagem_url": "/figurinhas_img/21-Paulo.avif", "papel": "Co-fundador da Alura"},
    {"id": 22, "nome": "Guilherme Silveira", "categoria": "Brasil", "imagem_url": "/figurinhas_img/22-Guilherme.jpeg", "papel": "Co-fundador da Alura"},
    {"id": 23, "nome": "Gustavo Guanabara", "categoria": "Brasil", "imagem_url": "/figurinhas_img/23-Gus.png", "papel": "Criador do Curso em Vídeo"},
    {"id": 24, "nome": "Maurício Aniche", "categoria": "Brasil", "imagem_url": "/figurinhas_img/24-Mauricio.jpeg", "papel": "Engenharia de Software / Educador"},
    {"id": 25, "nome": "Andre David", "categoria": "Brasil", "imagem_url": "/figurinhas_img/25-Andre.jpeg", "papel": "Coordenador da FIAP"},
    {"id": 26, "nome": "Guilherme Lima", "categoria": "Brasil", "imagem_url": "/figurinhas_img/26-Guilherme.jpeg", "papel": "Alura / Tech Educator"},
    {"id": 27, "nome": "Gi Space Coding", "categoria": "Brasil", "imagem_url": "/figurinhas_img/27-Gi.jpeg", "papel": "Giovanna Souza / Creator"},
    {"id": 28, "nome": "Vinicius Neves", "categoria": "Brasil", "imagem_url": "/figurinhas_img/28-Vinicius.png", "papel": "Desenvolvedor FullStack"},
    {"id": 29, "nome": "Rafaela Ballerini", "categoria": "Brasil", "imagem_url": "/figurinhas_img/29-Rafa.jpeg", "papel": "Alura / Tech Educator"},
    {"id": 30, "nome": "Pedro Zeferino", "categoria": "Brasil", "imagem_url": "/figurinhas_img/30-Pedro.jpeg", "papel": "Desenvolvedor"},
    {"id": 31, "nome": "James Gosling", "categoria": "Java", "imagem_url": "/figurinhas_img/31-gosling.jpg", "papel": "Criador da linguagem Java"},
    {"id": 32, "nome": "Patrick Naughton", "categoria": "Java", "imagem_url": "/figurinhas_img/32-naughton.jpg", "papel": "Cocriador do Java / Green Project"},
    {"id": 33, "nome": "Mike Sheridan", "categoria": "Java", "imagem_url": "/figurinhas_img/33-sheridan.jpg", "papel": "Cocriador do Java / Green Project"},
    {"id": 34, "nome": "Mark Reinhold", "categoria": "Java", "imagem_url": "/figurinhas_img/34-reinhold.jpg", "papel": "Arquiteto-chefe da plataforma Java"},
    {"id": 35, "nome": "Brian Goetz", "categoria": "Java", "imagem_url": "/figurinhas_img/35-goetz.jpg", "papel": "Arquiteto de linguagem Java na Oracle"},
    {"id": 36, "nome": "Brendan Eich", "categoria": "JavaScript", "imagem_url": "/figurinhas_img/36-brendan.jpg", "papel": "Criador da linguagem JavaScript"},
    {"id": 37, "nome": "Douglas Crockford", "categoria": "JavaScript", "imagem_url": "/figurinhas_img/37-crockford.jpg", "papel": "Popularizou o JSON e autor influente"},
    {"id": 38, "nome": "Ryan Dahl", "categoria": "JavaScript", "imagem_url": "/figurinhas_img/38-ryan.jpg", "papel": "Criador do runtime Node.js"},
    {"id": 39, "nome": "Anders Hejlsberg", "categoria": "JavaScript", "imagem_url": "/figurinhas_img/39-anders.jpg", "papel": "Criador do TypeScript e C#"},
    {"id": 40, "nome": "Jordan Walke", "categoria": "JavaScript", "imagem_url": "/figurinhas_img/40-jordan.jpg", "papel": "Criador da biblioteca React"}
]


def init_db():
    """Cria as tabelas (SQLite ou PostgreSQL) e insere as figurinhas iniciais se necessário."""
    metadata.create_all(engine)

    with engine.begin() as conn:
        count = conn.execute(select(func.count()).select_from(figurinhas)).scalar_one()
        if count == 0:
            logger.info("Semeando banco de dados com as figurinhas iniciais...")
            conn.execute(figurinhas.insert(), INITIAL_FIGURINHAS)
            logger.info("Semeadura concluída com sucesso.")


# --- SEGURANÇA E AUXILIARES DE USUÁRIO ---

def hash_password(password: str) -> str:
    """Gera o hash PBKDF2 SHA-256 seguro para a senha informada."""
    salt = os.urandom(16)
    db_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + db_hash.hex()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha coincide com o hash salvo."""
    try:
        salt_hex, hash_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        db_hash = bytes.fromhex(hash_hex)
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return test_hash == db_hash
    except Exception:
        return False


# --- FUNÇÕES DE OPERAÇÕES DE FIGURINHAS (CRUD) ---

def get_all_figurinhas(nome: str = None, categoria: str = None):
    """Retorna uma lista de todas as figurinhas cadastradas no sistema."""
    stmt = select(figurinhas)

    if categoria:
        stmt = stmt.where(func.lower(figurinhas.c.categoria) == categoria.lower())
    if nome:
        stmt = stmt.where(figurinhas.c.nome.ilike(f"%{nome}%"))

    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [dict(row) for row in rows]


def get_figurinha_by_id(figurinha_id: int):
    """Obtém os dados de uma figurinha específica pelo ID."""
    with engine.connect() as conn:
        row = conn.execute(
            select(figurinhas).where(figurinhas.c.id == figurinha_id)
        ).mappings().first()
    return dict(row) if row else None


# --- OPERAÇÕES DE USUÁRIO E ÁLBUM ---

def create_user(username: str, password_plain: str):
    """Cria um novo usuário com senha hashed no banco de dados."""
    password_hash = hash_password(password_plain)
    try:
        with engine.begin() as conn:
            result = conn.execute(
                users.insert().values(username=username, password_hash=password_hash)
            )
        user_id = result.inserted_primary_key[0]
        return {"id": user_id, "username": username}
    except IntegrityError:
        return None


def get_user_by_username(username: str):
    """Busca os dados do usuário pelo username."""
    with engine.connect() as conn:
        row = conn.execute(
            select(users).where(users.c.username == username)
        ).mappings().first()
    return dict(row) if row else None


def get_user_collected_stickers(user_id: int):
    """Retorna a lista de IDs das figurinhas que o usuário possui coladas."""
    with engine.connect() as conn:
        rows = conn.execute(
            select(user_figurinhas.c.figurinha_id).where(user_figurinhas.c.user_id == user_id)
        ).mappings().all()
    return [row["figurinha_id"] for row in rows]


def collect_sticker(user_id: int, figurinha_id: int) -> bool:
    """Cola/adiciona uma figurinha ao álbum de um usuário."""
    try:
        with engine.begin() as conn:
            conn.execute(
                user_figurinhas.insert().values(user_id=user_id, figurinha_id=figurinha_id)
            )
        return True
    except IntegrityError:
        return False  # Já colada ou figurinha inexistente


def uncollect_sticker(user_id: int, figurinha_id: int) -> bool:
    """Descola/remove uma figurinha do álbum de um usuário."""
    with engine.begin() as conn:
        result = conn.execute(
            user_figurinhas.delete().where(
                user_figurinhas.c.user_id == user_id,
                user_figurinhas.c.figurinha_id == figurinha_id,
            )
        )
    return result.rowcount > 0
