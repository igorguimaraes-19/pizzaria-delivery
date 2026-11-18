"""Testes de integração: rotas + banco PostgreSQL real.

Defina a variável DATABASE_URL_TESTE apontando para um banco VAZIO de testes
(as tabelas são apagadas e recriadas a cada teste). Sem ela, estes testes são pulados.

Exemplo:
    DATABASE_URL_TESTE=postgresql://postgres:senha@localhost:5432/pizzaria_teste pytest
"""
import os
from datetime import datetime
from decimal import Decimal

import pytest

from app import create_app, db, regras

URL_TESTE = os.environ.get("DATABASE_URL_TESTE")
pytestmark = pytest.mark.skipif(not URL_TESTE, reason="DATABASE_URL_TESTE não definida")

ENDERECO = {"logradouro": "Rua das Flores", "numero": "100", "complemento": "",
            "bairro": "Centro", "cidade": "São Paulo", "cep": "01001-000"}


@pytest.fixture()
def app(monkeypatch):
    # Por padrão, a pizzaria está aberta (sexta, 20:00)
    monkeypatch.setattr(regras, "agora_local", lambda: datetime(2026, 11, 20, 20, 0, 0))
    aplicacao = create_app({"TESTING": True, "DATABASE_URL": URL_TESTE})
    with aplicacao.app_context():
        db.recriar_banco()
    return aplicacao


def sql(app, consulta, params=(), um=False):
    with app.app_context():
        return db.consultar(consulta, params, um=um)


def novo_cliente(app, nome="Maria Silva", email="maria@email.com"):
    cliente = app.test_client()
    cliente.post("/cadastro", data={"nome": nome, "email": email,
                                    "telefone": "11999990000", "senha": "segredo1"})
    cliente.post("/login", data={"email": email, "senha": "segredo1"})
    cliente.post("/enderecos", data=ENDERECO)
    return cliente


def admin(app):
    cliente = app.test_client()
    cliente.post("/login", data={"email": "admin@pizzaria.com", "senha": "admin123"})
    return cliente


def fazer_pedido(cliente, id_produto=1, qtd=2, id_endereco=1, pagamento="PIX"):
    cliente.post("/carrinho/adicionar", data={"id_produto": id_produto, "quantidade": qtd})
    return cliente.post("/pedidos", data={"id_endereco": id_endereco,
                                          "forma_pagamento": pagamento}, follow_redirects=True)


def texto(resposta):
    return resposta.get_data(as_text=True)


# --- Cadastro e login (RF01, RF02, RN09) ---------------------------------------
def test_cadastro_e_email_duplicado(app):
    c = app.test_client()
    dados = {"nome": "Ana", "email": "ana@email.com", "telefone": "11", "senha": "123456"}
    assert c.post("/cadastro", data=dados).status_code == 302
    repetido = c.post("/cadastro", data=dados)
    assert repetido.status_code == 400
    assert "Este e-mail já está cadastrado" in texto(repetido)


def test_senha_fica_com_hash(app):
    novo_cliente(app)
    senha_hash = sql(app, "SELECT senha_hash FROM usuario WHERE email='maria@email.com'",
                     um=True)["senha_hash"]
    assert senha_hash != "segredo1" and len(senha_hash) > 30


def test_login_invalido_e_valido(app):
    c = app.test_client()
    ruim = c.post("/login", data={"email": "x@x.com", "senha": "errada"})
    assert ruim.status_code == 401 and "E-mail ou senha incorretos" in texto(ruim)
    novo_cliente(app)
    logado = app.test_client()
    logado.post("/login", data={"email": "maria@email.com", "senha": "segredo1"})
    assert "Sair (Maria)" in texto(logado.get("/cardapio"))


def test_rotas_protegidas(app):
    c = app.test_client()
    resp = c.get("/pedidos")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]
    cliente = novo_cliente(app)
    resp = cliente.get("/admin/pedidos", follow_redirects=True)
    assert "Você não tem permissão para acessar esta página." in texto(resp)


# --- Fluxo principal (RF05, RF07, RN05, RN06) -----------------------------------
def test_pedido_completo(app):
    cliente = novo_cliente(app)
    resp = fazer_pedido(cliente, id_produto=1, qtd=2)
    assert "Pedido nº 1 recebido" in texto(resp)
    pedido = sql(app, "SELECT * FROM pedido WHERE id_pedido = 1", um=True)
    assert pedido["status"] == "RECEBIDO"
    assert pedido["valor_total"] == Decimal("102.00")   # 2 x 48,00 + 6,00
    item = sql(app, "SELECT * FROM item_pedido WHERE id_pedido = 1", um=True)
    assert item["quantidade"] == 2 and item["preco_unitario"] == Decimal("48.00")
    assert ">0<" in texto(cliente.get("/cardapio")).replace(" ", "").replace("\n", "")  # carrinho zerou


def test_preco_do_item_nao_muda_quando_o_cardapio_muda(app):
    cliente = novo_cliente(app)
    fazer_pedido(cliente, id_produto=1, qtd=1)
    adm = admin(app)
    adm.post("/admin/produtos/1/editar", data={"nome": "Pizza Mussarela (Grande)", "descricao": "",
                                               "categoria": "PIZZA", "preco": "99,90"})
    item = sql(app, "SELECT preco_unitario FROM item_pedido WHERE id_pedido = 1", um=True)
    assert item["preco_unitario"] == Decimal("48.00")


def test_carrinho_atualiza_e_remove(app):
    c = novo_cliente(app)
    c.post("/carrinho/adicionar", data={"id_produto": 1, "quantidade": 1})
    c.post("/carrinho/atualizar", data={"id_produto": 1, "quantidade": 3})
    assert "R$ 150,00" in texto(c.get("/carrinho"))     # 3 x 48 + 6
    c.post("/carrinho/remover", data={"id_produto": 1})
    assert "Seu carrinho está vazio." in texto(c.get("/carrinho"))


def test_quantidade_acima_do_limite_e_recusada(app):
    c = novo_cliente(app)
    resp = c.post("/carrinho/adicionar", data={"id_produto": 1, "quantidade": 21},
                  follow_redirects=True)
    assert "quantidade deve ficar entre 1 e 20" in texto(resp)


# --- Regras de recusa do pedido (RN01, RN02, RN04, RN10) ------------------------
def test_pedido_fora_do_horario(app, monkeypatch):
    cliente = novo_cliente(app)
    monkeypatch.setattr(regras, "agora_local", lambda: datetime(2026, 11, 20, 15, 0, 0))
    resp = fazer_pedido(cliente)
    assert "Estamos fechados agora" in texto(resp)
    assert sql(app, "SELECT COUNT(*) AS n FROM pedido", um=True)["n"] == 0


def test_pedido_com_carrinho_vazio(app):
    cliente = novo_cliente(app)
    resp = cliente.post("/pedidos", data={"id_endereco": 1, "forma_pagamento": "PIX"},
                        follow_redirects=True)
    assert "Seu carrinho está vazio" in texto(resp)


def test_endereco_de_outro_cliente_e_recusado(app):
    novo_cliente(app)                                             # endereço id 1 é da Maria
    joao = novo_cliente(app, "João Souza", "joao@email.com")      # endereço id 2
    resp = fazer_pedido(joao, id_endereco=1)
    assert "Escolha um endereço de entrega" in texto(resp)
    assert sql(app, "SELECT COUNT(*) AS n FROM pedido", um=True)["n"] == 0


def test_produto_inativo_nao_pode_ser_pedido(app):
    cliente = novo_cliente(app)
    cliente.post("/carrinho/adicionar", data={"id_produto": 1, "quantidade": 1})
    admin(app).post("/admin/produtos/1/ativo")
    resp = cliente.post("/pedidos", data={"id_endereco": 1, "forma_pagamento": "PIX"},
                        follow_redirects=True)
    assert "não está mais disponível" in texto(resp)
    assert sql(app, "SELECT COUNT(*) AS n FROM pedido", um=True)["n"] == 0


# --- Status e cancelamento (RN07, RN08) ----------------------------------------------
def test_cliente_cancela_pedido_recebido(app):
    cliente = novo_cliente(app)
    fazer_pedido(cliente)
    resp = cliente.post("/pedidos/1/cancelar", follow_redirects=True)
    assert "Pedido cancelado com sucesso." in texto(resp)
    assert sql(app, "SELECT status FROM pedido WHERE id_pedido=1", um=True)["status"] == "CANCELADO"


def test_cliente_nao_cancela_pedido_em_preparo(app):
    cliente = novo_cliente(app)
    fazer_pedido(cliente)
    admin(app).post("/admin/pedidos/1/avancar")
    resp = cliente.post("/pedidos/1/cancelar", follow_redirects=True)
    assert "já está em preparo e não pode mais ser cancelado" in texto(resp)
    assert sql(app, "SELECT status FROM pedido WHERE id_pedido=1", um=True)["status"] == "EM_PREPARO"


def test_admin_cancela_pedido_em_preparo(app):
    cliente = novo_cliente(app)
    fazer_pedido(cliente)
    adm = admin(app)
    adm.post("/admin/pedidos/1/avancar")
    adm.post("/pedidos/1/cancelar")
    assert sql(app, "SELECT status FROM pedido WHERE id_pedido=1", um=True)["status"] == "CANCELADO"


def test_sequencia_completa_de_status(app):
    cliente = novo_cliente(app)
    fazer_pedido(cliente)
    adm = admin(app)
    for esperado in ("EM_PREPARO", "SAIU_PARA_ENTREGA", "ENTREGUE"):
        adm.post("/admin/pedidos/1/avancar")
        assert sql(app, "SELECT status FROM pedido WHERE id_pedido=1", um=True)["status"] == esperado
    resp = adm.post("/admin/pedidos/1/avancar", follow_redirects=True)
    assert "não pode mais mudar de status" in texto(resp)


def test_cliente_nao_acessa_pedido_de_outro(app):
    maria = novo_cliente(app)
    fazer_pedido(maria)
    joao = novo_cliente(app, "João Souza", "joao@email.com")
    assert joao.get("/pedidos/1").status_code == 404
    # tentar cancelar o pedido alheio é recusado (acaba na página 404) e nada muda
    assert joao.post("/pedidos/1/cancelar", follow_redirects=True).status_code == 404
    assert sql(app, "SELECT status FROM pedido WHERE id_pedido=1", um=True)["status"] == "RECEBIDO"


# --- Administração (RF03, RF11) --------------------------------------------------
def test_admin_cria_produto_e_recusa_preco_invalido(app):
    adm = admin(app)
    ok = adm.post("/admin/produtos/novo", data={"nome": "Pizza Teste", "descricao": "x",
                                                "categoria": "PIZZA", "preco": "39,90"})
    assert ok.status_code == 302
    assert sql(app, "SELECT preco FROM produto WHERE nome='Pizza Teste'", um=True)["preco"] == Decimal("39.90")
    ruim = adm.post("/admin/produtos/novo", data={"nome": "Outra", "descricao": "",
                                                  "categoria": "PIZZA", "preco": "-3"})
    assert "preço deve ser maior que zero" in texto(ruim)


def test_painel_mostra_pedidos_e_faturamento_sem_cancelados(app):
    cliente = novo_cliente(app)
    fazer_pedido(cliente, qtd=1)       # 54,00
    fazer_pedido(cliente, qtd=2)       # 102,00 (será cancelado)
    cliente.post("/pedidos/2/cancelar")
    painel = texto(admin(app).get("/admin/pedidos?data=2026-11-20"))
    assert "Maria Silva" in painel
    assert "R$ 54,00" in painel
    assert "Faturamento do dia (sem cancelados): <strong>R$ 54,00</strong>" in painel
