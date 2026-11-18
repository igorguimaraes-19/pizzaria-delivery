"""Model de usuários (clientes e administração)."""
import psycopg2.errors
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, regras


def criar(nome, email, telefone, senha, perfil="CLIENTE"):
    nome = regras.exigir(nome, "nome", 100)
    email = regras.validar_email(email)
    telefone = regras.exigir(telefone, "telefone", 20)
    regras.validar_senha(senha)
    try:
        linha = db.executar(
            "INSERT INTO usuario (nome, email, telefone, senha_hash, perfil) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id_usuario",
            (nome, email, telefone, generate_password_hash(senha), perfil),
            retornar=True,
        )
    except psycopg2.errors.UniqueViolation:  # RN09
        raise regras.RegraNegocioError(
            "Este e-mail já está cadastrado. Tente entrar ou use outro e-mail."
        )
    return linha["id_usuario"]


def buscar_por_id(id_usuario):
    return db.consultar("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,), um=True)


def buscar_por_email(email):
    return db.consultar(
        "SELECT * FROM usuario WHERE email = %s", ((email or "").strip().lower(),), um=True
    )


def autenticar(email, senha):
    """Devolve o usuário se e-mail e senha conferem; senão, None."""
    usuario = buscar_por_email(email)
    if usuario and check_password_hash(usuario["senha_hash"], senha or ""):
        return usuario
    return None
