"""Controller de endereços e pedidos do cliente (RF06 a RF10)."""
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from app import regras
from app.controllers.cardapio import itens_do_carrinho
from app.controllers.seguranca import login_obrigatorio
from app.models import endereco as endereco_model
from app.models import pedido as pedido_model
from app.regras import RegraNegocioError

bp = Blueprint("pedidos", __name__)


@bp.route("/enderecos", methods=["GET", "POST"])
@login_obrigatorio
def enderecos():
    if request.method == "POST":
        try:
            endereco_model.criar(
                session["usuario_id"], request.form.get("logradouro"), request.form.get("numero"),
                request.form.get("complemento"), request.form.get("bairro"),
                request.form.get("cidade"), request.form.get("cep"),
            )
            flash("Endereço cadastrado.", "sucesso")
            destino = request.form.get("voltar_para")
            return redirect(url_for("pedidos.finalizar") if destino == "finalizar"
                            else url_for("pedidos.enderecos"))
        except RegraNegocioError as erro:
            flash(str(erro), "erro")
    return render_template("enderecos.html",
                           enderecos=endereco_model.listar(session["usuario_id"]),
                           voltar_para=request.args.get("voltar_para", ""))


@bp.route("/pedido/finalizar")
@login_obrigatorio
def finalizar():
    itens = itens_do_carrinho()
    if not itens:
        flash("Seu carrinho está vazio. Adicione pelo menos um item.", "erro")
        return redirect(url_for("cardapio.ver_cardapio"))
    subtotal = sum((i["subtotal"] for i in itens), 0)
    return render_template("finalizar.html", itens=itens, subtotal=subtotal,
                           taxa=regras.TAXA_ENTREGA, total=subtotal + regras.TAXA_ENTREGA,
                           enderecos=endereco_model.listar(session["usuario_id"]),
                           formas=regras.FORMAS_PAGAMENTO)


@bp.route("/pedidos", methods=["GET", "POST"])
@login_obrigatorio
def pedidos():
    if request.method == "POST":
        carrinho = {int(k): v for k, v in session.get("carrinho", {}).items()}
        try:
            id_endereco = int(request.form.get("id_endereco", ""))
        except ValueError:
            flash("Escolha um endereço de entrega.", "erro")
            return redirect(url_for("pedidos.finalizar"))
        try:
            id_pedido = pedido_model.criar(
                session["usuario_id"], id_endereco, request.form.get("forma_pagamento"),
                carrinho, request.form.get("observacao"), agora=regras.agora_local(),
            )
        except RegraNegocioError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pedidos.finalizar"))
        session["carrinho"] = {}
        flash(f"Pedido nº {id_pedido} recebido! Acompanhe o andamento em Meus pedidos.", "sucesso")
        return redirect(url_for("pedidos.detalhe", id_pedido=id_pedido))
    return render_template("meus_pedidos.html",
                           pedidos=pedido_model.listar_do_usuario(session["usuario_id"]))


@bp.route("/pedidos/<int:id_pedido>")
@login_obrigatorio
def detalhe(id_pedido):
    pedido = pedido_model.buscar(id_pedido)
    eh_admin = session.get("usuario_perfil") == "ADMIN"
    if pedido is None or (not eh_admin and pedido["id_usuario"] != session["usuario_id"]):
        abort(404)
    return render_template("pedido_detalhe.html", pedido=pedido,
                           pode_cancelar=regras.pode_cancelar(
                               pedido["status"], session.get("usuario_perfil")))


@bp.route("/pedidos/<int:id_pedido>/cancelar", methods=["POST"])
@login_obrigatorio
def cancelar(id_pedido):
    try:
        pedido_model.cancelar(id_pedido, session.get("usuario_perfil"), session["usuario_id"])
        flash("Pedido cancelado com sucesso.", "sucesso")
    except RegraNegocioError as erro:
        flash(str(erro), "erro")
    return redirect(url_for("pedidos.detalhe", id_pedido=id_pedido))
