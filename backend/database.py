import os
import sqlite3
import hashlib
import logging

logger = logging.getLogger("alura-album-api")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album.db")

def get_db_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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
    """Inicializa as tabelas do banco de dados e insere as figurinhas iniciais se necessário."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Cria tabela de figurinhas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS figurinhas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT NOT NULL,
        imagem_url TEXT NOT NULL,
        papel TEXT NOT NULL
    )
    """)

    # Cria tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

    # Cria tabela associativa para o álbum do usuário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_figurinhas (
        user_id INTEGER NOT NULL,
        figurinha_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, figurinha_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (figurinha_id) REFERENCES figurinhas(id) ON DELETE CASCADE
    )
    """)

    # Semeia as figurinhas se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM figurinhas")
    count = cursor.fetchone()[0]
    if count == 0:
        logger.info("Semeando banco de dados com as figurinhas iniciais...")
        for f in INITIAL_FIGURINHAS:
            cursor.execute("""
            INSERT INTO figurinhas (id, nome, categoria, imagem_url, papel)
            VALUES (?, ?, ?, ?, ?)
            """, (f["id"], f["nome"], f["categoria"], f["imagem_url"], f["papel"]))
        conn.commit()
        logger.info("Semeadura concluída com sucesso.")
    
    conn.close()

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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM figurinhas WHERE 1=1"
    params = []
    
    if categoria:
        query += " AND LOWER(categoria) = LOWER(?)"
        params.append(categoria)
    if nome:
        query += " AND LOWER(nome) LIKE ?"
        params.append(f"%{nome.lower()}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_figurinha_by_id(figurinha_id: int):
    """Obtém os dados de uma figurinha específica pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM figurinhas WHERE id = ?", (figurinha_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_figurinha(nome: str, categoria: str, imagem_url: str, papel: str):
    """Cadastra uma nova figurinha no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO figurinhas (nome, categoria, imagem_url, papel)
    VALUES (?, ?, ?, ?)
    """, (nome, categoria, imagem_url, papel))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_figurinha_by_id(new_id)

def update_figurinha(figurinha_id: int, nome: str = None, categoria: str = None, imagem_url: str = None, papel: str = None):
    """Atualiza as informações de uma figurinha existente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    params = []
    
    if nome is not None:
        fields.append("nome = ?")
        params.append(nome)
    if categoria is not None:
        fields.append("categoria = ?")
        params.append(categoria)
    if imagem_url is not None:
        fields.append("imagem_url = ?")
        params.append(imagem_url)
    if papel is not None:
        fields.append("papel = ?")
        params.append(papel)
        
    if not fields:
        conn.close()
        return get_figurinha_by_id(figurinha_id)
        
    query = f"UPDATE figurinhas SET {', '.join(fields)} WHERE id = ?"
    params.append(figurinha_id)
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    return get_figurinha_by_id(figurinha_id)

def delete_figurinha(figurinha_id: int) -> bool:
    """Remove uma figurinha do banco de dados pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM figurinhas WHERE id = ?", (figurinha_id,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes > 0

# --- OPERAÇÕES DE USUÁRIO E ÁLBUM ---

def create_user(username: str, password_plain: str):
    """Cria um novo usuário com senha hashed no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password_plain)
    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
        """, (username, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "username": username}
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_username(username: str):
    """Busca os dados do usuário pelo username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_collected_stickers(user_id: int):
    """Retorna a lista de IDs das figurinhas que o usuário possui coladas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT figurinha_id FROM user_figurinhas WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row["figurinha_id"] for row in rows]

def collect_sticker(user_id: int, figurinha_id: int) -> bool:
    """Cola/adiciona uma figurinha ao álbum de um usuário."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO user_figurinhas (user_id, figurinha_id)
        VALUES (?, ?)
        """, (user_id, figurinha_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Já colada ou figurinha inexistente

def uncollect_sticker(user_id: int, figurinha_id: int) -> bool:
    """Descola/remove uma figurinha do álbum de um usuário."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM user_figurinhas WHERE user_id = ? AND figurinha_id = ?
    """, (user_id, figurinha_id))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes > 0
