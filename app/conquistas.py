from flask import Blueprint, render_template

from .models import Desejo

conquistas_bp = Blueprint("conquistas", __name__, url_prefix="/conquistas")


@conquistas_bp.route("/")
def listar():
    desejos = Desejo.query.order_by(Desejo.data_meta).all()
    conquistados = [d for d in desejos if d.meta_atingida]
    pendentes = [d for d in desejos if not d.meta_atingida]
    return render_template("conquistas.html", conquistados=conquistados, pendentes=pendentes)
