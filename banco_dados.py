import sqlite3
import hashlib
import os

def conectar():
    return sqlite3.connect("sistema_financeiro.db")

def configurar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha_hash BLOB NOT NULL,
        salt BLOB NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saldo_conta (
        usuario_id INTEGER PRIMARY KEY,
        saldo_base REAL DEFAULT 0.0,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        categoria TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        banco TEXT NOT NULL,
        valor_fatura REAL NOT NULL,
        vencimento TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

def cadastrar_usuario(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    salt = os.urandom(16)
    senha_fusa = salt + senha.encode('utf-8')
    senha_hash = hashlib.sha256(senha_fusa).digest()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha_hash, salt) VALUES (?, ?, ?)", (usuario, senha_hash, salt))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def obter_id_autenticado(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, senha_hash, salt FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        user_id, armazenado_hash, salt = resultado
        senha_fusa = salt + senha.encode('utf-8')
        gabarito_hash = hashlib.sha256(senha_fusa).digest()
        if armazenado_hash == gabarito_hash:
            return user_id
    return None

def obter_nome_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM usuarios WHERE id = ?", (usuario_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "Desconhecido"

def carregar_saldo_base(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT saldo_base FROM saldo_conta WHERE usuario_id = ?", (usuario_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0.0

def adicionar_fundos_banco(usuario_id, valor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT saldo_base FROM saldo_conta WHERE usuario_id = ?", (usuario_id,))
    if cursor.fetchone():
        cursor.execute("UPDATE saldo_conta SET saldo_base = saldo_base + ? WHERE usuario_id = ?", (valor, usuario_id))
    else:
        cursor.execute("INSERT INTO saldo_conta (usuario_id, saldo_base) VALUES (?, ?)", (usuario_id, valor))
    conn.commit()
    conn.close()

def inserir_transacao(usuario_id, descricao, valor, categoria):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transacoes (usuario_id, descricao, valor, categoria) VALUES (?, ?, ?, ?)", (usuario_id, descricao, valor, categoria))
    conn.commit()
    conn.close()

def obter_gastos_filtrados(usuario_id, filtro):
    conn = conectar()
    cursor = conn.cursor()
    if filtro == "Todos":
        cursor.execute("SELECT descricao, valor, categoria, id FROM transacoes WHERE usuario_id = ?", (usuario_id,))
    else:
        cursor.execute("SELECT descricao, valor, categoria, id FROM transacoes WHERE usuario_id = ? AND categoria = ?", (usuario_id, filtro))
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_total_gastos(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE usuario_id = ?", (usuario_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado[0] is not None else 0.0

def deletar_transacao(id_transacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
    conn.commit()
    conn.close()

def inserir_cartao(usuario_id, banco, valor_fatura, vencimento):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cartoes (usuario_id, banco, valor_fatura, vencimento) VALUES (?, ?, ?, ?)", (usuario_id, banco, valor_fatura, vencimento))
    conn.commit()
    conn.close()

def obter_todos_cartoes(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT banco, valor_fatura, id, vencimento FROM cartoes WHERE usuario_id = ?", (usuario_id,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_total_faturas(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_fatura) FROM cartoes WHERE usuario_id = ?", (usuario_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado[0] is not None else 0.0

def deletar_cartao(id_cartao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cartoes WHERE id = ?", (id_cartao,))
    conn.commit()
    conn.close()

def obter_cartao_por_id(id_cartao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT banco, valor_fatura FROM cartoes WHERE id = ?", (id_cartao,))
    dado = cursor.fetchone()
    conn.close()
    return dado

def reiniciar_dados_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saldo_conta WHERE usuario_id = ?", (usuario_id,))
    cursor.execute("DELETE FROM transacoes WHERE usuario_id = ?", (usuario_id,))
    cursor.execute("DELETE FROM cartoes WHERE usuario_id = ?", (usuario_id,))
    conn.commit()
    conn.close()

# --- NOVO MÉTODO PARA O GRÁFICO DE PIZZA ---
def obter_gastos_por_categoria(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    # Agrupa e soma os valores da mesma categoria (ignorando depósitos)
    cursor.execute("SELECT categoria, SUM(valor) FROM transacoes WHERE usuario_id = ? GROUP BY categoria", (usuario_id,))
    dados = cursor.fetchall()
    conn.close()
    return dados