import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "CubeMaker3D_Management.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas caso ainda nao existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS filamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_id INTEGER NOT NULL,
            cor_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            diametro_mm REAL NOT NULL,
            peso_rolo_g REAL NOT NULL,
            quantidade_rolos INTEGER NOT NULL,
            FOREIGN KEY (marca_id) REFERENCES marcas (id),
            FOREIGN KEY (cor_id) REFERENCES cores (id),
            FOREIGN KEY (material_id) REFERENCES materiais (id)
        )
    """)

    conn.commit()
    conn.close()


def inserir_simples(tabela, nome):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {tabela} (nome) VALUES (?)", (nome,))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_simples(tabela):
    conn = get_connection()
    linhas = conn.execute(f"SELECT * FROM {tabela} ORDER BY nome ASC").fetchall()
    conn.close()
    return [dict(l) for l in linhas]


def buscar_simples(tabela, item_id):
    conn = get_connection()
    linha = conn.execute(f"SELECT * FROM {tabela} WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(linha) if linha else None


def atualizar_simples(tabela, item_id, nome):
    conn = get_connection()
    conn.execute(f"UPDATE {tabela} SET nome = ? WHERE id = ?", (nome, item_id))
    conn.commit()
    conn.close()


def deletar_simples(tabela, item_id):
    conn = get_connection()
    conn.execute(f"DELETE FROM {tabela} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def contar_filamentos_usando(coluna_fk, item_id):
    """Conta quantos filamentos referenciam uma marca/cor/material especifica."""
    conn = get_connection()
    total = conn.execute(
        f"SELECT COUNT(*) as total FROM filamentos WHERE {coluna_fk} = ?", (item_id,)
    ).fetchone()["total"]
    conn.close()
    return total


def inserir_filamento(marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO filamentos (marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_filamentos():
    conn = get_connection()
    linhas = conn.execute("""
        SELECT filamentos.*, marcas.nome AS marca_nome, cores.nome AS cor_nome, materiais.nome AS material_nome
        FROM filamentos
        JOIN marcas ON filamentos.marca_id = marcas.id
        JOIN cores ON filamentos.cor_id = cores.id
        JOIN materiais ON filamentos.material_id = materiais.id
        ORDER BY filamentos.id DESC
    """).fetchall()
    conn.close()
    return [dict(l) for l in linhas]


def buscar_filamento(filamento_id):
    conn = get_connection()
    linha = conn.execute("SELECT * FROM filamentos WHERE id = ?", (filamento_id,)).fetchone()
    conn.close()
    return dict(linha) if linha else None


def atualizar_filamento(filamento_id, marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos):
    conn = get_connection()
    conn.execute(
        """UPDATE filamentos
           SET marca_id = ?, cor_id = ?, material_id = ?, diametro_mm = ?, peso_rolo_g = ?, quantidade_rolos = ?
           WHERE id = ?""",
        (marca_id, cor_id, material_id, diametro_mm, peso_rolo_g, quantidade_rolos, filamento_id)
    )
    conn.commit()
    conn.close()


def deletar_filamento(filamento_id):
    conn = get_connection()
    conn.execute("DELETE FROM filamentos WHERE id = ?", (filamento_id,))
    conn.commit()
    conn.close()
