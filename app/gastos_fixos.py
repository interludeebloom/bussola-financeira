from datetime import date

from flask import Blueprint, jsonify, request

from . import db
from .models import GastoFixo, PagamentoFixo

fixos_bp = Blueprint("fixos", __name__, url_prefix="/api/gastos-fixos")


@fixos_bp.route("/")
def listar():
    hoje = date.today()
    ano, mes = hoje.year, hoje.month

    gastos = GastoFixo.query.filter_by(ativo=True).order_by(GastoFixo.dia_vencimento).all()

    itens = [g.to_dict(ano=ano, mes=mes) for g in gastos]
    total_previsto = sum(g.valor for g in gastos)
    total_pago = sum(g.valor for g, item in zip(gastos, itens) if item["pago"])

    return jsonify({
        "itens": itens,
        "total_previsto": total_previsto,
        "total_pago": total_pago,
        "ano": ano,
        "mes": mes,
    })


@fixos_bp.route("/", methods=["POST"])
def criar():
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    gasto = GastoFixo(
        nome=dados["nome"].strip(),
        valor=float(dados["valor"]),
        dia_vencimento=int(dados["dia_vencimento"]),
    )
    db.session.add(gasto)
    db.session.commit()
    return jsonify(gasto.to_dict()), 201


@fixos_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    gasto = GastoFixo.query.get_or_404(id)
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    gasto.nome = dados["nome"].strip()
    gasto.valor = float(dados["valor"])
    gasto.dia_vencimento = int(dados["dia_vencimento"])
    db.session.commit()
    return jsonify(gasto.to_dict())


@fixos_bp.route("/<int:id>", methods=["DELETE"])
def excluir(id):
    gasto = GastoFixo.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    return "", 204


@fixos_bp.route("/<int:id>/pagar", methods=["POST"])
def pagar(id):
    GastoFixo.query.get_or_404(id)
    hoje = date.today()
    ano, mes = hoje.year, hoje.month

    pagamento = PagamentoFixo.query.filter_by(gasto_fixo_id=id, ano=ano, mes=mes).first()
    if pagamento is None:
        pagamento = PagamentoFixo(gasto_fixo_id=id, ano=ano, mes=mes)
        db.session.add(pagamento)

    pagamento.pago = True
    pagamento.data_pagamento = hoje
    db.session.commit()
    return jsonify({"pago": True})


@fixos_bp.route("/<int:id>/desfazer", methods=["POST"])
def desfazer(id):
    hoje = date.today()
    ano, mes = hoje.year, hoje.month

    pagamento = PagamentoFixo.query.filter_by(gasto_fixo_id=id, ano=ano, mes=mes).first()
    if pagamento:
        pagamento.pago = False
        pagamento.data_pagamento = None
        db.session.commit()
    return jsonify({"pago": False})


def _validar(dados):
    nome = (dados.get("nome") or "").strip()
    valor = dados.get("valor", "")
    dia_vencimento = dados.get("dia_vencimento", "")

    if not nome:
        return "Nome é obrigatório."
    try:
        if float(valor) <= 0:
            return "Valor precisa ser maior que zero."
    except (TypeError, ValueError):
        return "Valor inválido."
    try:
        dia = int(dia_vencimento)
        if not 1 <= dia <= 31:
            return "Dia de vencimento precisa ser entre 1 e 31."
    except (TypeError, ValueError):
        return "Dia de vencimento inválido."
    return None
