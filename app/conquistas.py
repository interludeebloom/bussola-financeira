from flask import Blueprint, jsonify

from .models import Desejo

conquistas_bp = Blueprint("conquistas", __name__, url_prefix="/api/conquistas")


@conquistas_bp.route("/")
def listar():
    desejos = Desejo.query.order_by(Desejo.data_meta).all()
    conquistados = [d.to_dict() for d in desejos if d.meta_atingida]
    pendentes = [d.to_dict() for d in desejos if not d.meta_atingida]
    return jsonify({"conquistados": conquistados, "pendentes": pendentes})
