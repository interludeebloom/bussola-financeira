from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .models import GastoFixo, PagamentoFixo

fixos_bp = Blueprint("fixos", __name__, url_prefix="/gastos-fixos")

NOMES_MESES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


@fixos_bp.route("/")
def listar():
    hoje = date.today()
    ano, mes = hoje.year, hoje.month

    gastos = GastoFixo.query.filter_by(ativo=True).order_by(GastoFixo.dia_vencimento).all()

    itens = []
    total_previsto = 0.0
    total_pago = 0.0
    for gasto in gastos:
        pagamento = gasto.pagamento_do_mes(ano, mes)
        pago = bool(pagamento and pagamento.pago)
        total_previsto += gasto.valor
        if pago:
            total_pago += gasto.valor
        itens.append({"gasto": gasto, "pago": pago})

    return render_template(
        "gastos_fixos.html",
        itens=itens,
        total_previsto=total_previsto,
        total_pago=total_pago,
        nome_mes=NOMES_MESES[mes],
        ano=ano,
    )


@fixos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro)
            return render_template("form_gasto_fixo.html", gasto=None, valores=_valores_de_form(request.form)), 400

        gasto = GastoFixo(
            nome=request.form["nome"].strip(),
            valor=float(request.form["valor"]),
            dia_vencimento=int(request.form["dia_vencimento"]),
        )
        db.session.add(gasto)
        db.session.commit()
        return redirect(url_for("fixos.listar"))

    return render_template("form_gasto_fixo.html", gasto=None, valores=_valores_padrao())


@fixos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    gasto = GastoFixo.query.get_or_404(id)

    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro)
            return render_template("form_gasto_fixo.html", gasto=gasto, valores=_valores_de_form(request.form)), 400

        gasto.nome = request.form["nome"].strip()
        gasto.valor = float(request.form["valor"])
        gasto.dia_vencimento = int(request.form["dia_vencimento"])
        db.session.commit()
        return redirect(url_for("fixos.listar"))

    return render_template("form_gasto_fixo.html", gasto=gasto, valores=_valores_de_gasto(gasto))


@fixos_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    gasto = GastoFixo.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    return redirect(url_for("fixos.listar"))


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
    return redirect(url_for("fixos.listar"))


@fixos_bp.route("/<int:id>/desfazer", methods=["POST"])
def desfazer(id):
    hoje = date.today()
    ano, mes = hoje.year, hoje.month

    pagamento = PagamentoFixo.query.filter_by(gasto_fixo_id=id, ano=ano, mes=mes).first()
    if pagamento:
        pagamento.pago = False
        pagamento.data_pagamento = None
        db.session.commit()
    return redirect(url_for("fixos.listar"))


def _validar_formulario(form):
    nome = form.get("nome", "").strip()
    valor = form.get("valor", "")
    dia_vencimento = form.get("dia_vencimento", "")

    if not nome:
        return "Nome é obrigatório."
    try:
        if float(valor) <= 0:
            return "Valor precisa ser maior que zero."
    except ValueError:
        return "Valor inválido."
    try:
        dia = int(dia_vencimento)
        if not 1 <= dia <= 31:
            return "Dia de vencimento precisa ser entre 1 e 31."
    except ValueError:
        return "Dia de vencimento inválido."
    return None


def _valores_padrao():
    return {"nome": "", "valor": "", "dia_vencimento": ""}


def _valores_de_gasto(gasto):
    return {"nome": gasto.nome, "valor": gasto.valor, "dia_vencimento": gasto.dia_vencimento}


def _valores_de_form(form):
    return {
        "nome": form.get("nome", ""),
        "valor": form.get("valor", ""),
        "dia_vencimento": form.get("dia_vencimento", ""),
    }
