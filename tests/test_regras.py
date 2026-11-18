"""Testes unitários das regras de negócio (não precisam de banco de dados)."""
from datetime import datetime
from decimal import Decimal

import pytest

from app import regras
from app.regras import RegraNegocioError


# --- RN02: horário de funcionamento ---------------------------------------
@pytest.mark.parametrize("hora, minuto, esperado", [
    (17, 59, False), (18, 0, True), (20, 30, True), (23, 30, True), (23, 31, False), (3, 0, False),
])
def test_horario_de_funcionamento(hora, minuto, esperado):
    assert regras.esta_aberto(datetime(2026, 11, 20, hora, minuto)) is esperado


def test_validar_aberto_recusa_fora_do_horario():
    with pytest.raises(RegraNegocioError, match="fechados") as erro:
        regras.validar_aberto(datetime(2026, 11, 20, 12, 0))
    assert regras.texto_horario() in str(erro.value)


# --- RN01: quantidade ------------------------------------------------------
@pytest.mark.parametrize("valor, esperado", [("1", 1), (20, 20), ("5", 5)])
def test_quantidade_valida(valor, esperado):
    assert regras.validar_quantidade(valor) == esperado


@pytest.mark.parametrize("valor", [0, 21, -1, "abc", None, ""])
def test_quantidade_invalida(valor):
    with pytest.raises(RegraNegocioError):
        regras.validar_quantidade(valor)


# --- RN05: cálculo do total ------------------------------------------------
def test_total_soma_itens_e_taxa():
    itens = [(2, Decimal("48.00")), (1, Decimal("12.00"))]
    assert regras.calcular_total(itens) == Decimal("114.00")  # 96 + 12 + 6


def test_total_com_taxa_personalizada():
    assert regras.calcular_total([(1, Decimal("10.00"))], taxa=Decimal("0")) == Decimal("10.00")


def test_total_arredonda_em_duas_casas():
    assert regras.calcular_total([(3, Decimal("3.333"))], taxa=Decimal("0")) == Decimal("10.00")


def test_total_sem_itens_e_recusado():
    with pytest.raises(RegraNegocioError, match="vazio"):
        regras.calcular_total([])


# --- RN07: sequência de status --------------------------------------------
def test_sequencia_de_status():
    assert regras.proximo_status("RECEBIDO") == "EM_PREPARO"
    assert regras.proximo_status("EM_PREPARO") == "SAIU_PARA_ENTREGA"
    assert regras.proximo_status("SAIU_PARA_ENTREGA") == "ENTREGUE"


@pytest.mark.parametrize("status", ["ENTREGUE", "CANCELADO", "INVENTADO"])
def test_status_final_nao_avanca(status):
    with pytest.raises(RegraNegocioError):
        regras.proximo_status(status)


# --- RN08: cancelamento ----------------------------------------------------
@pytest.mark.parametrize("status, perfil, esperado", [
    ("RECEBIDO", "CLIENTE", True),
    ("EM_PREPARO", "CLIENTE", False),
    ("SAIU_PARA_ENTREGA", "CLIENTE", False),
    ("RECEBIDO", "ADMIN", True),
    ("EM_PREPARO", "ADMIN", True),
    ("SAIU_PARA_ENTREGA", "ADMIN", False),
    ("ENTREGUE", "ADMIN", False),
    ("CANCELADO", "ADMIN", False),
])
def test_quem_pode_cancelar(status, perfil, esperado):
    assert regras.pode_cancelar(status, perfil) is esperado


def test_validar_cancelamento_levanta_erro():
    with pytest.raises(RegraNegocioError, match="não pode mais ser cancelado"):
        regras.validar_cancelamento("EM_PREPARO", "CLIENTE")


# --- Validações de entrada -------------------------------------------------
def test_cep():
    assert regras.normalizar_cep("01001-000") == "01001000"
    for invalido in ("123", "abcdefgh", "", None):
        with pytest.raises(RegraNegocioError, match="CEP"):
            regras.normalizar_cep(invalido)


def test_email():
    assert regras.validar_email("  Ana@Email.COM ") == "ana@email.com"
    for invalido in ("semarroba", "a@b", "", None):
        with pytest.raises(RegraNegocioError):
            regras.validar_email(invalido)


def test_senha_minima():
    assert regras.validar_senha("123456") == "123456"
    for curta in ("12345", "", None):
        with pytest.raises(RegraNegocioError):
            regras.validar_senha(curta)


def test_campo_obrigatorio():
    assert regras.exigir("  Rua A ", "rua") == "Rua A"
    with pytest.raises(RegraNegocioError, match="Preencha o campo rua"):
        regras.exigir("   ", "rua")
    with pytest.raises(RegraNegocioError, match="até 5"):
        regras.exigir("abcdef", "rua", 5)


def test_preco():
    assert regras.validar_preco("49,90") == Decimal("49.90")
    assert regras.validar_preco("10") == Decimal("10.00")
    for invalido in ("0", "-5", "abc", ""):
        with pytest.raises(RegraNegocioError):
            regras.validar_preco(invalido)


def test_forma_pagamento_e_categoria():
    assert regras.validar_forma_pagamento("PIX") == "PIX"
    with pytest.raises(RegraNegocioError):
        regras.validar_forma_pagamento("FIADO")
    assert regras.validar_categoria("PIZZA") == "PIZZA"
    with pytest.raises(RegraNegocioError):
        regras.validar_categoria("CARRO")
