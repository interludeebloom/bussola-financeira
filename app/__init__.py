import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bussola.db")
    app.config["SECRET_KEY"] = "dev"

    db.init_app(app)

    from . import models
    from .dashboard import dashboard_bp
    from .desejos import desejos_bp
    from .faturas import faturas_bp
    from .gastos_fixos import fixos_bp
    from .routes import main_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(fixos_bp)
    app.register_blueprint(desejos_bp)
    app.register_blueprint(faturas_bp)

    with app.app_context():
        db.create_all()
        _migrar_colunas_novas()

    return app


def _migrar_colunas_novas():
    """Adiciona colunas novas em tabelas ja existentes, sem apagar dados.

    Nao usamos Flask-Migrate neste projeto (seria complexidade a mais pra
    fase atual), entao quando um Column novo e adicionado a um model cujo
    banco local ja existe, o SQLite precisa desse ALTER TABLE manual.
    """
    inspector = inspect(db.engine)
    if "transacao" not in inspector.get_table_names():
        return
    colunas = {c["name"] for c in inspector.get_columns("transacao")}
    if "categoria" not in colunas:
        db.session.execute(text("ALTER TABLE transacao ADD COLUMN categoria VARCHAR(40)"))
        db.session.commit()
