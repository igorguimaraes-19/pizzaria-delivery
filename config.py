"""Configurações da aplicação. Os valores sensíveis vêm de variáveis de ambiente."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Em produção (Render), defina SECRET_KEY e DATABASE_URL nas variáveis de ambiente.
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pizzaria"
    )
    # Conta de administração criada automaticamente na primeira execução
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@pizzaria.com")
    ADMIN_SENHA = os.environ.get("ADMIN_SENHA", "admin123")
    ADMIN_NOME = "Administração"
    # Carrega o cardápio de exemplo quando o banco é criado pela primeira vez
    CARREGAR_DADOS_EXEMPLO = os.environ.get("CARREGAR_DADOS_EXEMPLO", "1") == "1"
    SCHEMA_SQL = BASE_DIR / "banco" / "schema.sql"
    DADOS_SQL = BASE_DIR / "banco" / "dados_exemplo.sql"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    TESTING = False
