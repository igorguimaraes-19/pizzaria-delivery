"""Model de pedidos: criação, consulta, mudança de status e cancelamento."""
from app import db, regras
from app.models import endereco as endereco_model
from app.models import produto as produto_model


def criar(id_usuario, id_endereco, forma_pagamento, carrinho, observacao=None, agora=None):
    """Cria o pedido e seus itens em uma única transação.

    `carrinho` é um dicionário {id_produto: quantidade}.
    Aplica RN01, RN02, RN04, RN05, RN06 e RN10.
    """
    agora = agora or regras.agora_local()
    regras.validar_aberto(agora)                                     # RN02
    if not carrinho:                                                 # RN01
        raise regras.RegraNegocioError("Seu carrinho está vazio. Adicione pelo menos um item.")
    regras.validar_forma_pagamento(forma_pagamento)
    if not endereco_model.buscar(id_endereco, id_usuario):           # RN10
        raise regras.RegraNegocioError("Escolha um endereço de entrega.")

    produtos = {p["id_produto"]: p for p in produto_model.buscar_varios(carrinho.keys())}
    itens = []
    for id_produto, qtd in carrinho.items():
        produto = produtos.get(id_produto)
        if produto is None or not produto["ativo"]:                  # RN04
            nome = produto["nome"] if produto else "selecionado"
            raise regras.RegraNegocioError(
                f"O item {nome} não está mais disponível. Remova-o do carrinho."
            )
        itens.append((id_produto, regras.validar_quantidade(qtd), produto["preco"]))  # RN01, RN06

    total = regras.calcular_total([(q, p) for _, q, p in itens])     # RN05
    observacao = (observacao or "").strip()[:255] or None

    conn = db.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pedido (id_usuario, id_endereco, data_hora, forma_pagamento, "
                "taxa_entrega, valor_total, observacao) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_pedido",
                (id_usuario, id_endereco, agora, forma_pagamento,
                 regras.TAXA_ENTREGA, total, observacao),
            )
            id_pedido = cur.fetchone()["id_pedido"]
            for id_produto, qtd, preco in itens:
                cur.execute(
                    "INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario) "
                    "VALUES (%s, %s, %s, %s)",
                    (id_pedido, id_produto, qtd, preco),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return id_pedido


def buscar(id_pedido):
    """Pedido com cliente, endereço e itens."""
    pedido = db.consultar(
        "SELECT pe.*, u.nome AS cliente, u.telefone, e.logradouro, e.numero, e.complemento, "
        "e.bairro, e.cidade, e.cep "
        "FROM pedido pe "
        "JOIN usuario u ON u.id_usuario = pe.id_usuario "
        "JOIN endereco e ON e.id_endereco = pe.id_endereco "
        "WHERE pe.id_pedido = %s",
        (id_pedido,),
        um=True,
    )
    if pedido:
        pedido["itens"] = db.consultar(
            "SELECT p.nome, i.quantidade, i.preco_unitario, "
            "i.quantidade * i.preco_unitario AS subtotal "
            "FROM item_pedido i JOIN produto p ON p.id_produto = i.id_produto "
            "WHERE i.id_pedido = %s ORDER BY p.nome",
            (id_pedido,),
        )
    return pedido


def listar_do_usuario(id_usuario):
    return db.consultar(
        "SELECT id_pedido, data_hora, status, forma_pagamento, valor_total "
        "FROM pedido WHERE id_usuario = %s ORDER BY data_hora DESC",
        (id_usuario,),
    )


def listar_por_filtro(data, status=None):
    """Painel da administração: pedidos de um dia, opcionalmente filtrados por status."""
    sql = (
        "SELECT pe.id_pedido, pe.data_hora, pe.status, pe.valor_total, u.nome AS cliente, "
        "u.telefone, e.logradouro, e.numero, e.bairro "
        "FROM pedido pe "
        "JOIN usuario u ON u.id_usuario = pe.id_usuario "
        "JOIN endereco e ON e.id_endereco = pe.id_endereco "
        "WHERE pe.data_hora::date = %s"
    )
    params = [data]
    if status:
        sql += " AND pe.status = %s"
        params.append(status)
    return db.consultar(sql + " ORDER BY pe.data_hora", params)


def faturamento_do_dia(data):
    linha = db.consultar(
        "SELECT COALESCE(SUM(valor_total), 0) AS total FROM pedido "
        "WHERE data_hora::date = %s AND status <> 'CANCELADO'",
        (data,),
        um=True,
    )
    return linha["total"]


def avancar_status(id_pedido):
    """RN07: move o pedido para o próximo status da sequência."""
    pedido = db.consultar("SELECT status FROM pedido WHERE id_pedido = %s", (id_pedido,), um=True)
    if pedido is None:
        raise regras.RegraNegocioError("Pedido não encontrado.")
    novo = regras.proximo_status(pedido["status"])
    db.executar("UPDATE pedido SET status = %s WHERE id_pedido = %s", (novo, id_pedido))
    return novo


def cancelar(id_pedido, perfil, id_usuario=None):
    """RN08. Cliente só cancela o próprio pedido, enquanto RECEBIDO."""
    pedido = db.consultar(
        "SELECT status, id_usuario FROM pedido WHERE id_pedido = %s", (id_pedido,), um=True
    )
    if pedido is None or (perfil != "ADMIN" and pedido["id_usuario"] != id_usuario):
        raise regras.RegraNegocioError("Pedido não encontrado.")
    regras.validar_cancelamento(pedido["status"], perfil)
    db.executar("UPDATE pedido SET status = 'CANCELADO' WHERE id_pedido = %s", (id_pedido,))
