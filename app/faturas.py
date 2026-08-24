from datetime import date, datetime

from flask import Blueprint, jsonify, request

from . import db
from .models import Banco, Fatura, GastoFatura
from .utils import NOMES_MESES

faturas_bp = Blueprint("faturas", __name__, url_prefix="/api/faturas")
bancos_bp = Blueprint("bancos", __name__, url_prefix="/api/bancos")


@faturas_bp.route("/")
def ver():
    hoje = date.today()

    banco_id = request.args.get("banco_id", type=int)
    ano = request.args.get("ano", type=int) or hoje.year
    mes = request.args.get("mes", type=int) or hoje.month

    fatura = None
    if banco_id:
        fatura = Fatura.query.filter_by(banco_id=banco_id, ano=ano, mes=mes).first()

    gastos = fatura.gastos if fatura else []
    total = fatura.total if fatura else 0.0

    return jsonify({
        "banco_id": banco_id,
        "ano": ano,
        "mes": mes,
        "nome_mes": NOMES_MESES[mes],
        "gastos": [g.to_dict() for g in gastos],
        "total": total,
    })


@faturas_bp.route("/gastos", methods=["POST"])
def novo_gasto():
    dados = request.get_json(silent=True) or {}
    banco_id = dados.get("banco_id")
    ano = dados.get("ano")
    mes = dados.get("mes")

    erro = _validar_gasto(dados, banco_id, ano, mes)
    if erro:
        return jsonify({"erro": erro}), 400

    fatura = Fatura.query.filter_by(banco_id=banco_id, ano=ano, mes=mes).first()
    if fatura is None:
        fatura = Fatura(banco_id=banco_id, ano=ano, mes=mes)
        db.session.add(fatura)
        db.session.flush()

    data_raw = (dados.get("data") or "").strip()
    data_gasto = datetime.strptime(data_raw, "%Y-%m-%d").date() if data_raw else None

    gasto = GastoFatura(
        fatura_id=fatura.id,
        descricao=dados["descricao"].strip(),
        valor=float(dados["valor"]),
        data=data_gasto,
    )
    db.session.add(gasto)
    db.session.commit()
    return jsonify(gasto.to_dict()), 201


@faturas_bp.route("/gastos/<int:id>", methods=["DELETE"])
def excluir_gasto(id):
    gasto = GastoFatura.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    return "", 204


@bancos_bp.route("/")
def listar():
    lista = Banco.query.order_by(Banco.nome).all()
    return jsonify([b.to_dict() for b in lista])


@bancos_bp.route("/", methods=["POST"])
def criar():
    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "Nome do banco é obrigatório."}), 400
    if Banco.query.filter_by(nome=nome).first():
        return jsonify({"erro": "Já existe um banco com esse nome."}), 400

    banco = Banco(nome=nome)
    db.session.add(banco)
    db.session.commit()
    return jsonify(banco.to_dict()), 201


@bancos_bp.route("/<int:id>", methods=["DELETE"])
def excluir(id):
    banco = Banco.query.get_or_404(id)
    db.session.delete(banco)
    db.session.commit()
    return "", 204


def _validar_gasto(dados, banco_id, ano, mes):
    if not banco_id or not Banco.query.get(banco_id):
        return "Selecione um banco válido."
    if not ano or not mes or not 1 <= mes <= 12:
        return "Mês/ano inválido."
    if not (dados.get("descricao") or "").strip():
        return "Descrição é obrigatória."
    valor = dados.get("valor", "")
    try:
        if float(valor) <= 0:
            return "Valor precisa ser maior que zero."
    except (TypeError, ValueError):
        return "Valor inválido."
    data_raw = (dados.get("data") or "").strip()
    if data_raw:
        try:
            datetime.strptime(data_raw, "%Y-%m-%d")
        except ValueError:
            return "Data inválida."
    return None
