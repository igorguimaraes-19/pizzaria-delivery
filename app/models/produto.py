"""Model do cardápio."""
import psycopg2.errors

from app import db, regras


def listar_ativos(categoria=None):
    if categoria in regras.CATEGORIAS:
        return db.consultar(
            "SELECT * FROM produto WHERE ativo AND categoria = %s ORDER BY nome", (categoria,)
        )
    return db.consultar("SELECT * FROM produto WHERE ativo ORDER BY categoria, nome")


def listar_todos():
    return db.consultar("SELECT * FROM produto ORDER BY ativo DESC, categoria, nome")


def buscar(id_produto):
    return db.consultar("SELECT * FROM produto WHERE id_produto = %s", (id_produto,), um=True)


def buscar_varios(ids):
    if not ids:
        return []
    return db.consultar("SELECT * FROM produto WHERE id_produto = ANY(%s)", (list(ids),))


def _validar(nome, descricao, categoria, preco):
    return (
        regras.exigir(nome, "nome", 100),
        (descricao or "").strip()[:255] or None,
        regras.validar_categoria(categoria),
        regras.validar_preco(preco),
    )


def criar(nome, descricao, categoria, preco):
    dados = _validar(nome, descricao, categoria, preco)
    try:
        linha = db.executar(
            "INSERT INTO produto (nome, descricao, categoria, preco) "
            "VALUES (%s, %s, %s, %s) RETURNING id_produto",
            dados,
            retornar=True,
        )
    except psycopg2.errors.UniqueViolation:
        raise regras.RegraNegocioError("Já existe um produto com este nome.")
    return linha["id_produto"]


def atualizar(id_produto, nome, descricao, categoria, preco):
    dados = _validar(nome, descricao, categoria, preco)
    try:
        db.executar(
            "UPDATE produto SET nome = %s, descricao = %s, categoria = %s, preco = %s "
            "WHERE id_produto = %s",
            dados + (id_produto,),
        )
    except psycopg2.errors.UniqueViolation:
        raise regras.RegraNegocioError("Já existe um produto com este nome.")


def alternar_ativo(id_produto):
    """Inativa ou reativa o produto (nunca exclui, para preservar o histórico)."""
    db.executar("UPDATE produto SET ativo = NOT ativo WHERE id_produto = %s", (id_produto,))
