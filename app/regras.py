"""Regras de negócio puras (sem banco e sem Flask), fáceis de testar.

Cada função aplica uma regra do README (RN01 a RN10).
"""
import os
import re
from datetime import datetime, time
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def _hora(texto, padrao):
    """Lê um horário HH:MM de uma variável de ambiente; usa o padrão se estiver inválido."""
    try:
        hora, minuto = str(texto).split(":")
        return time(int(hora), int(minuto))
    except (ValueError, AttributeError):
        return padrao


# RN02: padrão 18:00 às 23:30; pode ser mudado por HORARIO_ABERTURA / HORARIO_FECHAMENTO
ABERTURA = _hora(os.environ.get("HORARIO_ABERTURA", "18:00"), time(18, 0))
FECHAMENTO = _hora(os.environ.get("HORARIO_FECHAMENTO", "23:30"), time(23, 30))
TAXA_ENTREGA = Decimal("6.00")  # RN03
QTD_MIN, QTD_MAX = 1, 20      # RN01

CATEGORIAS = ("PIZZA", "BEBIDA", "SOBREMESA", "OUTROS")
FORMAS_PAGAMENTO = ("DINHEIRO", "CARTAO", "PIX")

# RN07: sequência permitida de status
PROXIMO_STATUS = {
    "RECEBIDO": "EM_PREPARO",
    "EM_PREPARO": "SAIU_PARA_ENTREGA",
    "SAIU_PARA_ENTREGA": "ENTREGUE",
}
ROTULO_STATUS = {
    "RECEBIDO": "Recebido",
    "EM_PREPARO": "Em preparo",
    "SAIU_PARA_ENTREGA": "Saiu para entrega",
    "ENTREGUE": "Entregue",
    "CANCELADO": "Cancelado",
}


class RegraNegocioError(Exception):
    """Erro de regra de negócio; a mensagem é segura para mostrar ao usuário."""


def agora_local() -> datetime:
    """Data e hora atuais em Brasília, sem fuso (como gravamos no banco)."""
    return datetime.now(FUSO).replace(tzinfo=None, microsecond=0)


def esta_aberto(momento: datetime) -> bool:
    """RN02: pedidos aceitos das 18:00 às 23:30."""
    return ABERTURA <= momento.time() <= FECHAMENTO


def texto_horario() -> str:
    return f"das {ABERTURA:%H:%M} às {FECHAMENTO:%H:%M}"


def validar_aberto(momento: datetime) -> None:
    if not esta_aberto(momento):
        raise RegraNegocioError(f"Estamos fechados agora. Recebemos pedidos {texto_horario()}.")


def validar_quantidade(valor) -> int:
    """RN01: quantidade inteira entre 1 e 20."""
    try:
        qtd = int(valor)
    except (TypeError, ValueError):
        raise RegraNegocioError("Informe uma quantidade válida.")
    if not QTD_MIN <= qtd <= QTD_MAX:
        raise RegraNegocioError(f"A quantidade deve ficar entre {QTD_MIN} e {QTD_MAX}.")
    return qtd


def calcular_total(itens, taxa: Decimal = TAXA_ENTREGA) -> Decimal:
    """RN05: soma de quantidade x preço unitário + taxa de entrega.

    `itens` é uma lista de pares (quantidade, preco_unitario).
    """
    if not itens:
        raise RegraNegocioError("Seu carrinho está vazio. Adicione pelo menos um item.")  # RN01
    subtotal = sum((Decimal(q) * Decimal(p) for q, p in itens), Decimal("0"))
    return (subtotal + Decimal(taxa)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def proximo_status(atual: str) -> str:
    """RN07: devolve o próximo status ou levanta erro se não houver."""
    if atual not in PROXIMO_STATUS:
        raise RegraNegocioError("Este pedido não pode mais mudar de status.")
    return PROXIMO_STATUS[atual]


def pode_cancelar(status: str, perfil: str) -> bool:
    """RN08: cliente cancela só RECEBIDO; administração cancela RECEBIDO ou EM_PREPARO."""
    if perfil == "ADMIN":
        return status in ("RECEBIDO", "EM_PREPARO")
    return status == "RECEBIDO"


def validar_cancelamento(status: str, perfil: str) -> None:
    if not pode_cancelar(status, perfil):
        raise RegraNegocioError(
            "Este pedido já está em preparo e não pode mais ser cancelado. "
            "Entre em contato com a pizzaria."
        )


def validar_forma_pagamento(forma: str) -> str:
    if forma not in FORMAS_PAGAMENTO:
        raise RegraNegocioError("Escolha uma forma de pagamento.")
    return forma


def normalizar_cep(cep: str) -> str:
    digitos = re.sub(r"\D", "", cep or "")
    if len(digitos) != 8:
        raise RegraNegocioError("Informe um CEP com 8 números.")
    return digitos


def validar_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise RegraNegocioError("Informe um e-mail válido.")
    return email


def validar_senha(senha: str) -> str:
    if not senha or len(senha) < 6:
        raise RegraNegocioError("A senha deve ter pelo menos 6 caracteres.")
    return senha


def exigir(valor: str, rotulo: str, maximo: int = 255) -> str:
    """Campo de texto obrigatório e com tamanho máximo."""
    valor = (valor or "").strip()
    if not valor:
        raise RegraNegocioError(f"Preencha o campo {rotulo}.")
    if len(valor) > maximo:
        raise RegraNegocioError(f"O campo {rotulo} aceita até {maximo} caracteres.")
    return valor


def validar_preco(valor) -> Decimal:
    try:
        preco = Decimal(str(valor).replace(",", ".")).quantize(Decimal("0.01"))
    except Exception:
        raise RegraNegocioError("Informe um preço válido, como 49,90.")
    if preco <= 0 or preco >= Decimal("100000"):
        raise RegraNegocioError("O preço deve ser maior que zero.")
    return preco


def validar_categoria(categoria: str) -> str:
    if categoria not in CATEGORIAS:
        raise RegraNegocioError("Escolha uma categoria válida.")
    return categoria
