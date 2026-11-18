"""Controller da administração: pedidos e cardápio (RF03, RF11, RF12)."""
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app import regras
from app.controllers.seguranca import admin_obrigatorio
from app.models import pedido as pedido_model
from app.models import produto as produto_model
from app.regras import RegraNegocioError

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/pedidos")
@admin_obrigatorio
def painel_pedidos():
    try:
        dia = date.fromisoformat(request.args.get("data", ""))
    except ValueError:
        dia = regras.agora_local().date()
    status = request.args.get("status", "")
    if status not in regras.ROTULO_STATUS:
        status = ""
    return render_template("admin_pedidos.html", pedidos=pedido_model.listar_por_filtro(dia, status),
                           dia=dia.isoformat(), status=status,
                           faturamento=pedido_model.faturamento_do_dia(dia))


@bp.route("/pedidos/<int:id_pedido>/avancar", methods=["POST"])
@admin_obrigatorio
def avancar(id_pedido):
    try:
        novo = pedido_model.avancar_status(id_pedido)
        flash(f"Pedido nº {id_pedido} agora está: {regras.ROTULO_STATUS[novo]}.", "sucesso")
    except RegraNegocioError as erro:
        flash(str(erro), "erro")
    return redirect(request.referrer or url_for("admin.painel_pedidos"))


@bp.route("/produtos")
@admin_obrigatorio
def produtos():
    return render_template("admin_produtos.html", produtos=produto_model.listar_todos())


@bp.route("/produtos/novo", methods=["GET", "POST"])
@bp.route("/produtos/<int:id_produto>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def formulario_produto(id_produto=None):
    produto = produto_model.buscar(id_produto) if id_produto else None
    if id_produto and produto is None:
        abort(404)
    if request.method == "POST":
        campos = (request.form.get("nome"), request.form.get("descricao"),
                  request.form.get("categoria"), request.form.get("preco"))
        try:
            if id_produto:
                produto_model.atualizar(id_produto, *campos)
            else:
                produto_model.criar(*campos)
            flash("Produto salvo.", "sucesso")
            return redirect(url_for("admin.produtos"))
        except RegraNegocioError as erro:
            flash(str(erro), "erro")
            produto = dict(zip(("nome", "descricao", "categoria", "preco"), campos))
    return render_template("admin_produto_form.html", produto=produto,
                           categorias=regras.CATEGORIAS)


@bp.route("/produtos/<int:id_produto>/ativo", methods=["POST"])
@admin_obrigatorio
def alternar_ativo(id_produto):
    produto_model.alternar_ativo(id_produto)
    flash("Disponibilidade do produto atualizada.", "sucesso")
    return redirect(url_for("admin.produtos"))
