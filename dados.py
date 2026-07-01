import sqlite3
import os

os.makedirs("arquivos", exist_ok=True)
CAMINHO_DB = "arquivos/biblioteca.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_DB)
    conexao.row_factory = sqlite3.Row
    return conexao


def executar(query, parametros=()):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(query, parametros)

    if query.strip().upper().startswith("SELECT"):
        resultado = [dict(linha) for linha in cursor.fetchall()]
    else:
        conexao.commit()
        resultado = cursor.rowcount

    conexao.close()
    return resultado


def init_db():
    executar("""
        CREATE TABLE IF NOT EXISTS livros (
            isbn TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER,
            genero TEXT,
            status TEXT NOT NULL DEFAULT 'disponivel'
        )
    """)


if __name__ == "__main__":
    init_db()
    print(f"Banco criado em: {os.path.abspath(CAMINHO_DB)}")
