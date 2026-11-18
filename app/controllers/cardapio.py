"""Controller do cardápio e do carrinho (RF04, RF05). O carrinho vive na sessão."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import regras
from app.models import produto as produto_model
from app.regras import RegraNegocioError

bp = Blueprint("cardapio", __name__)


def _carrinho():
    """Dicionário {id_produto(str): quantidade} guardado na sessão."""
    return session.setdefault("carrinho", {})


def itens_do_carrinho():
    """Une o carrinho da sessão aos dados atuais do banco."""
    carrinho = _carrinho()
    ids = [int(i) for i in carrinho]
    produtos = {p["id_produto"]: p for p in produto_model.buscar_varios(ids)}
    itens, removidos = [], False
    for id_str, qtd in list(carrinho.items()):
        produto = produtos.get(int(id_str))
        if produto is None or not produto["ativo"]:        # RN04
            del carrinho[id_str]
            removidos = True
            flash(f"O item {produto['nome'] if produto else 'selecionado'} "
                  "não está mais disponível e foi removido do carrinho.", "erro")
            continue
        itens.append({"produto": produto, "quantidade": qtd,
                      "subtotal": produto["preco"] * qtd})
    if removidos:
        session.modified = True
    return itens


@bp.route("/")
def inicio():
    return redirect(url_for("cardapio.ver_cardapio"))


@bp.route("/cardapio")
def ver_cardapio():
    categoria = request.args.get("categoria", "")
    produtos = produto_model.listar_ativos(categoria)
    return render_template("cardapio.html", produtos=produtos, categoria=categoria,
                           categorias=regras.CATEGORIAS, aberto=regras.esta_aberto(regras.agora_local()))


@bp.route("/carrinho")
def ver_carrinho():
    itens = itens_do_carrinho()
    subtotal = sum((i["subtotal"] for i in itens), 0)
    return render_template("carrinho.html", itens=itens, subtotal=subtotal,
                           taxa=regras.TAXA_ENTREGA, total=subtotal + regras.TAXA_ENTREGA)


@bp.route("/carrinho/adicionar", methods=["POST"])
def adicionar():
    try:
        id_produto = int(request.form.get("id_produto", ""))
        produto = produto_model.buscar(id_produto)
        if produto is None or not produto["ativo"]:
            raise RegraNegocioError("Este item não está disponível.")
        carrinho = _carrinho()
        nova_qtd = carrinho.get(str(id_produto), 0) + regras.validar_quantidade(
            request.form.get("quantidade", 1))
        carrinho[str(id_produto)] = regras.validar_quantidade(nova_qtd)
        session.modified = True
        flash(f"{produto['nome']} adicionado ao carrinho.", "sucesso")
    except (RegraNegocioError, ValueError) as erro:
        flash(str(erro) if isinstance(erro, RegraNegocioError) else "Item inválido.", "erro")
    return redirect(request.referrer or url_for("cardapio.ver_cardapio"))


@bp.route("/carrinho/atualizar", methods=["POST"])
def atualizar():
    id_str = request.form.get("id_produto", "")
    carrinho = _carrinho()
    if id_str in carrinho:
        try:
            carrinho[id_str] = regras.validar_quantidade(request.form.get("quantidade"))
            session.modified = True
        except RegraNegocioError as erro:
            flash(str(erro), "erro")
    return redirect(url_for("cardapio.ver_carrinho"))


@bp.route("/carrinho/remover", methods=["POST"])
def remover():
    _carrinho().pop(request.form.get("id_produto", ""), None)
    session.modified = True
    flash("Item removido do carrinho.", "sucesso")
    return redirect(url_for("cardapio.ver_carrinho"))
