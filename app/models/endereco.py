"""Model de endereços de entrega."""
from app import db, regras


def listar(id_usuario):
    return db.consultar(
        "SELECT * FROM endereco WHERE id_usuario = %s ORDER BY id_endereco", (id_usuario,)
    )


def buscar(id_endereco, id_usuario):
    """RN10: só devolve o endereço se ele pertencer ao usuário."""
    return db.consultar(
        "SELECT * FROM endereco WHERE id_endereco = %s AND id_usuario = %s",
        (id_endereco, id_usuario),
        um=True,
    )


def criar(id_usuario, logradouro, numero, complemento, bairro, cidade, cep):
    logradouro = regras.exigir(logradouro, "rua", 120)
    numero = regras.exigir(numero, "número", 10)
    complemento = (complemento or "").strip()[:60] or None
    bairro = regras.exigir(bairro, "bairro", 60)
    cidade = regras.exigir(cidade, "cidade", 60)
    cep = regras.normalizar_cep(cep)
    linha = db.executar(
        "INSERT INTO endereco (id_usuario, logradouro, numero, complemento, bairro, cidade, cep) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_endereco",
        (id_usuario, logradouro, numero, complemento, bairro, cidade, cep),
        retornar=True,
    )
    return linha["id_endereco"]
