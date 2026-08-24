from datetime import datetime

from flask import Blueprint, jsonify, request

from . import db
from .models import Transacao
from .utils import CATEGORIAS_DESPESA

main_bp = Blueprint("main", __name__, url_prefix="/api/transacoes")

TIPOS_VALIDOS = ("receita", "despesa")


@main_bp.route("/")
def listar():
    transacoes = Transacao.query.order_by(Transacao.data.desc(), Transacao.id.desc()).all()
    saldo = sum(t.valor_com_sinal for t in transacoes)
    return jsonify({
        "transacoes": [t.to_dict() for t in transacoes],
        "saldo": saldo,
        "categorias": CATEGORIAS_DESPESA,
    })


@main_bp.route("/", methods=["POST"])
def criar():
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    transacao = Transacao(
        descricao=dados["descricao"].strip(),
        valor=float(dados["valor"]),
        tipo=dados["tipo"],
        data=datetime.strptime(dados["data"], "%Y-%m-%d").date(),
        categoria=_categoria_para_salvar(dados),
    )
    db.session.add(transacao)
    db.session.commit()
    return jsonify(transacao.to_dict()), 201


@main_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    transacao = Transacao.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    transacao.descricao = dados["descricao"].strip()
    transacao.valor = float(dados["valor"])
    transacao.tipo = dados["tipo"]
    transacao.data = datetime.strptime(dados["data"], "%Y-%m-%d").date()
    transacao.categoria = _categoria_para_salvar(dados)
    db.session.commit()
    return jsonify(transacao.to_dict())


@main_bp.route("/<int:id>", methods=["DELETE"])
def excluir(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    return "", 204


def _categoria_para_salvar(dados):
    """Categoria so faz sentido pra despesa; receita sempre fica sem categoria."""
    if dados.get("tipo") != "despesa":
        return None
    return (dados.get("categoria") or "").strip() or None


def _validar(dados):
    descricao = (dados.get("descricao") or "").strip()
    valor = dados.get("valor", "")
    tipo = dados.get("tipo", "")
    data = dados.get("data", "")
    categoria = dados.get("categoria", "")

    if not descricao:
        return "Descrição é obrigatória."
    if tipo not in TIPOS_VALIDOS:
        return "Tipo precisa ser receita ou despesa."
    if tipo == "despesa" and categoria not in CATEGORIAS_DESPESA:
        return "Selecione uma categoria válida para a despesa."
    try:
        if float(valor) <= 0:
            return "Valor precisa ser maior que zero."
    except (TypeError, ValueError):
        return "Valor inválido."
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except (TypeError, ValueError):
        return "Data inválida."
    return None
