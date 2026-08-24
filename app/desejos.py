from datetime import datetime

from flask import Blueprint, jsonify, request

from . import db
from .models import Desejo

desejos_bp = Blueprint("desejos", __name__, url_prefix="/api/metas")


@desejos_bp.route("/")
def listar():
    desejos = Desejo.query.order_by(Desejo.data_meta).all()
    return jsonify([d.to_dict() for d in desejos])


@desejos_bp.route("/", methods=["POST"])
def criar():
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    desejo = Desejo(
        nome=dados["nome"].strip(),
        preco=float(dados["preco"]),
        data_meta=datetime.strptime(dados["data_meta"], "%Y-%m-%d").date(),
    )
    db.session.add(desejo)
    db.session.commit()
    return jsonify(desejo.to_dict()), 201


@desejos_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    desejo = Desejo.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    desejo.nome = dados["nome"].strip()
    desejo.preco = float(dados["preco"])
    desejo.data_meta = datetime.strptime(dados["data_meta"], "%Y-%m-%d").date()
    db.session.commit()
    return jsonify(desejo.to_dict())


@desejos_bp.route("/<int:id>", methods=["DELETE"])
def excluir(id):
    desejo = Desejo.query.get_or_404(id)
    db.session.delete(desejo)
    db.session.commit()
    return "", 204


@desejos_bp.route("/<int:id>/guardar", methods=["POST"])
def guardar(id):
    desejo = Desejo.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}
    try:
        valor = float(dados.get("valor", 0))
    except (TypeError, ValueError):
        valor = 0

    if valor <= 0:
        return jsonify({"erro": "Informe um valor maior que zero para guardar."}), 400

    desejo.guardado += valor
    db.session.commit()
    return jsonify(desejo.to_dict())


def _validar(dados):
    nome = (dados.get("nome") or "").strip()
    preco = dados.get("preco", "")
    data_meta = dados.get("data_meta", "")

    if not nome:
        return "Nome é obrigatório."
    try:
        if float(preco) <= 0:
            return "Preço precisa ser maior que zero."
    except (TypeError, ValueError):
        return "Preço inválido."
    try:
        datetime.strptime(data_meta, "%Y-%m-%d")
    except (TypeError, ValueError):
        return "Data da meta inválida."
    return None
