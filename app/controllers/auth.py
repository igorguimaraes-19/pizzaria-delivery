"""Controller de autenticação: cadastro, login e logout (RF01, RF02)."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models import usuario as usuario_model
from app.regras import RegraNegocioError

bp = Blueprint("auth", __name__)


def _abrir_sessao(usuario):
    carrinho = session.get("carrinho", {})
    session.clear()
    session["carrinho"] = carrinho
    session["usuario_id"] = usuario["id_usuario"]
    session["usuario_nome"] = usuario["nome"].split()[0]
    session["usuario_perfil"] = usuario["perfil"]


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        try:
            usuario_model.criar(
                request.form.get("nome"), request.form.get("email"),
                request.form.get("telefone"), request.form.get("senha"),
            )
        except RegraNegocioError as erro:
            flash(str(erro), "erro")
            return render_template("cadastro.html", dados=request.form), 400
        flash("Cadastro realizado! Entre com seu e-mail e senha.", "sucesso")
        return redirect(url_for("auth.login"))
    return render_template("cadastro.html", dados={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = usuario_model.autenticar(request.form.get("email"), request.form.get("senha"))
        if usuario is None:
            flash("E-mail ou senha incorretos.", "erro")
            return render_template("login.html", email=request.form.get("email", "")), 401
        _abrir_sessao(usuario)
        if usuario["perfil"] == "ADMIN":
            return redirect(url_for("admin.painel_pedidos"))
        return redirect(url_for("cardapio.ver_cardapio"))
    return render_template("login.html", email="")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("auth.login"))
