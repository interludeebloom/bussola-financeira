from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .models import Banco, Fatura, GastoFatura
from .utils import NOMES_MESES

faturas_bp = Blueprint("faturas", __name__, url_prefix="/faturas")


@faturas_bp.route("/")
def ver():
    hoje = date.today()
    bancos = Banco.query.order_by(Banco.nome).all()

    banco_id = request.args.get("banco_id", type=int)
    ano = request.args.get("ano", type=int) or hoje.year
    mes = request.args.get("mes", type=int) or hoje.month

    if banco_id is None and bancos:
        banco_id = bancos[0].id

    fatura = None
    if banco_id:
        fatura = Fatura.query.filter_by(banco_id=banco_id, ano=ano, mes=mes).first()

    gastos = fatura.gastos if fatura else []
    total = fatura.total if fatura else 0.0

    return render_template(
        "faturas.html",
        bancos=bancos,
        banco_id=banco_id,
        ano=ano,
        mes=mes,
        nomes_meses=NOMES_MESES,
        gastos=gastos,
        total=total,
    )


@faturas_bp.route("/gasto/novo", methods=["POST"])
def novo_gasto():
    banco_id = request.form.get("banco_id", type=int)
    ano = request.form.get("ano", type=int)
    mes = request.form.get("mes", type=int)

    erro = _validar_gasto(request.form, banco_id, ano, mes)
    if erro:
        flash(erro)
        return redirect(url_for("faturas.ver", banco_id=banco_id, ano=ano, mes=mes))

    fatura = Fatura.query.filter_by(banco_id=banco_id, ano=ano, mes=mes).first()
    if fatura is None:
        fatura = Fatura(banco_id=banco_id, ano=ano, mes=mes)
        db.session.add(fatura)
        db.session.flush()

    data_raw = request.form.get("data", "").strip()
    data_gasto = datetime.strptime(data_raw, "%Y-%m-%d").date() if data_raw else None

    gasto = GastoFatura(
        fatura_id=fatura.id,
        descricao=request.form["descricao"].strip(),
        valor=float(request.form["valor"]),
        data=data_gasto,
    )
    db.session.add(gasto)
    db.session.commit()
    return redirect(url_for("faturas.ver", banco_id=banco_id, ano=ano, mes=mes))


@faturas_bp.route("/gasto/excluir/<int:id>", methods=["POST"])
def excluir_gasto(id):
    gasto = GastoFatura.query.get_or_404(id)
    fatura = gasto.fatura
    banco_id, ano, mes = fatura.banco_id, fatura.ano, fatura.mes
    db.session.delete(gasto)
    db.session.commit()
    return redirect(url_for("faturas.ver", banco_id=banco_id, ano=ano, mes=mes))


@faturas_bp.route("/bancos")
def bancos():
    lista = Banco.query.order_by(Banco.nome).all()
    return render_template("bancos.html", bancos=lista)


@faturas_bp.route("/bancos/novo", methods=["POST"])
def novo_banco():
    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("Nome do banco é obrigatório.")
    elif Banco.query.filter_by(nome=nome).first():
        flash("Já existe um banco com esse nome.")
    else:
        db.session.add(Banco(nome=nome))
        db.session.commit()
    return redirect(url_for("faturas.bancos"))


@faturas_bp.route("/bancos/excluir/<int:id>", methods=["POST"])
def excluir_banco(id):
    banco = Banco.query.get_or_404(id)
    db.session.delete(banco)
    db.session.commit()
    return redirect(url_for("faturas.bancos"))


def _validar_gasto(form, banco_id, ano, mes):
    if not banco_id or not Banco.query.get(banco_id):
        return "Selecione um banco válido."
    if not ano or not mes or not 1 <= mes <= 12:
        return "Mês/ano inválido."
    if not form.get("descricao", "").strip():
        return "Descrição é obrigatória."
    valor = form.get("valor", "")
    try:
        if float(valor) <= 0:
            return "Valor precisa ser maior que zero."
    except ValueError:
        return "Valor inválido."
    data_raw = form.get("data", "").strip()
    if data_raw:
        try:
            datetime.strptime(data_raw, "%Y-%m-%d")
        except ValueError:
            return "Data inválida."
    return None
