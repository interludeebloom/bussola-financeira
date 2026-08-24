from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bussola.db"
    app.config["SECRET_KEY"] = "dev"

    db.init_app(app)

    from . import models
    from .desejos import desejos_bp
    from .gastos_fixos import fixos_bp
    from .routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(fixos_bp)
    app.register_blueprint(desejos_bp)

    with app.app_context():
        db.create_all()

    return app
