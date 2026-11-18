"""Decoradores de acesso por sessão e perfil."""
from functools import wraps

from flask import flash, redirect, session, url_for


def login_obrigatorio(rota):
    @wraps(rota)
    def interna(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Entre na sua conta para continuar.", "erro")
            return redirect(url_for("auth.login"))
        return rota(*args, **kwargs)
    return interna


def admin_obrigatorio(rota):
    @wraps(rota)
    @login_obrigatorio
    def interna(*args, **kwargs):
        if session.get("usuario_perfil") != "ADMIN":
            flash("Você não tem permissão para acessar esta página.", "erro")
            return redirect(url_for("cardapio.ver_cardapio"))
        return rota(*args, **kwargs)
    return interna
