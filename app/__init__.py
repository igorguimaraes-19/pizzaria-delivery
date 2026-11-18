"""Fábrica da aplicação Flask (padrão MVC: models, controllers e templates)."""
import secrets
from decimal import Decimal

from flask import Flask, abort, render_template, request, session

from app import db, regras
from config import Config


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    app.teardown_appcontext(db.fechar_conn)

    # --- Controllers (Blueprints) ---
    from app.controllers import admin, auth, cardapio, pedidos

    for modulo in (auth, cardapio, pedidos, admin):
        app.register_blueprint(modulo.bp)

    # --- Proteção CSRF simples: todo POST precisa do token da sessão ---
    @app.before_request
    def verificar_csrf():
        if request.method == "POST" and not app.config.get("TESTING"):
            token = session.get("csrf")
            if not token or token != request.form.get("csrf"):
                abort(400)

    @app.context_processor
    def contexto_global():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        carrinho = session.get("carrinho", {})
        return {
            "csrf_token": session["csrf"],
            "qtd_carrinho": sum(carrinho.values()),
            "usuario_nome": session.get("usuario_nome"),
            "usuario_perfil": session.get("usuario_perfil"),
            "rotulo_status": regras.ROTULO_STATUS,
            "horario_texto": regras.texto_horario(),
        }

    # --- Filtros de formatação ---
    @app.template_filter("brl")
    def brl(valor):
        valor = Decimal(valor or 0)
        texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    @app.template_filter("data_hora")
    def data_hora(valor):
        return valor.strftime("%d/%m/%Y %H:%M")

    # --- Tratamento de erros (RNF05) ---
    @app.errorhandler(400)
    def erro_400(_):
        return render_template("erro.html", titulo="Requisição inválida",
                               mensagem="Não foi possível processar a solicitação. "
                                        "Volte e tente novamente."), 400

    @app.errorhandler(404)
    def erro_404(_):
        return render_template("erro.html", titulo="Página não encontrada",
                               mensagem="A página que você procura não existe."), 404

    @app.errorhandler(500)
    def erro_500(_):
        return render_template("erro.html", titulo="Algo deu errado",
                               mensagem="Algo deu errado. Tente novamente em instantes."), 500

    # Cria as tabelas na primeira execução (não roda nos testes)
    if not app.config.get("TESTING"):
        with app.app_context():
            db.inicializar_banco_se_necessario()

    return app
