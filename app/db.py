"""Acesso ao PostgreSQL. Uma conexão por requisição, guardada em `flask.g`."""
import psycopg2
import psycopg2.extras
from flask import current_app, g


def _url() -> str:
    url = current_app.config["DATABASE_URL"]
    # Alguns provedores entregam "postgres://", que o psycopg2 não aceita
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_conn():
    if "conn" not in g:
        g.conn = psycopg2.connect(_url(), cursor_factory=psycopg2.extras.RealDictCursor)
    return g.conn


def fechar_conn(erro=None):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.rollback()  # descarta qualquer transação que não tenha recebido commit
        conn.close()


def consultar(sql, params=(), um=False):
    """SELECT: devolve uma linha (um=True) ou uma lista de linhas."""
    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone() if um else cur.fetchall()


def executar(sql, params=(), retornar=False):
    """INSERT/UPDATE/DELETE com commit. Com retornar=True devolve a linha do RETURNING."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            linha = cur.fetchone() if retornar else None
        conn.commit()
        return linha
    except Exception:
        conn.rollback()
        raise


def _rodar_arquivo(caminho):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(caminho.read_text(encoding="utf-8"))
    conn.commit()


def recriar_banco():
    """Apaga e recria todas as tabelas. Usado nos testes e na primeira execução."""
    from app.models import usuario

    cfg = current_app.config
    _rodar_arquivo(cfg["SCHEMA_SQL"])
    if cfg["CARREGAR_DADOS_EXEMPLO"]:
        _rodar_arquivo(cfg["DADOS_SQL"])
    usuario.criar(cfg["ADMIN_NOME"], cfg["ADMIN_EMAIL"], "00000000000",
                  cfg["ADMIN_SENHA"], perfil="ADMIN")


def inicializar_banco_se_necessario():
    """Cria as tabelas na primeira execução (o plano grátis do Render não tem terminal)."""
    existe = consultar("SELECT to_regclass('public.usuario') AS t", um=True)["t"]
    if existe is None:
        recriar_banco()
