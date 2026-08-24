from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .models import Transacao
from .utils import CATEGORIAS_DESPESA

main_bp = Blueprint("main", __name__, url_prefix="/transacoes")

TIPOS_VALIDOS = ("receita", "despesa")


@main_bp.route("/")
def index():
    transacoes = Transacao.query.order_by(Transacao.data.desc(), Transacao.id.desc()).all()
    saldo = sum(t.valor_com_sinal for t in transacoes)
    return render_template("index.html", transacoes=transacoes, saldo=saldo)


@main_bp.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro)
            return render_template(
                "form.html", transacao=None, valores=_valores_de_form(request.form), categorias=CATEGORIAS_DESPESA
            ), 400

        transacao = Transacao(
            descricao=request.form["descricao"].strip(),
            valor=float(request.form["valor"]),
            tipo=request.form["tipo"],
            data=datetime.strptime(request.form["data"], "%Y-%m-%d").date(),
            categoria=_categoria_para_salvar(request.form),
        )
        db.session.add(transacao)
        db.session.commit()
        return redirect(url_for("main.index"))

    return render_template("form.html", transacao=None, valores=_valores_padrao(), categorias=CATEGORIAS_DESPESA)


@main_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    transacao = Transacao.query.get_or_404(id)

    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro)
            return render_template(
                "form.html", transacao=transacao, valores=_valores_de_form(request.form), categorias=CATEGORIAS_DESPESA
            ), 400

        transacao.descricao = request.form["descricao"].strip()
        transacao.valor = float(request.form["valor"])
        transacao.tipo = request.form["tipo"]
        transacao.data = datetime.strptime(request.form["data"], "%Y-%m-%d").date()
        transacao.categoria = _categoria_para_salvar(request.form)
        db.session.commit()
        return redirect(url_for("main.index"))

    return render_template(
        "form.html", transacao=transacao, valores=_valores_de_transacao(transacao), categorias=CATEGORIAS_DESPESA
    )


@main_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    return redirect(url_for("main.index"))


def _categoria_para_salvar(form):
    """Categoria so faz sentido pra despesa; receita sempre fica sem categoria."""
    if form.get("tipo") != "despesa":
        return None
    return form.get("categoria", "").strip() or None


def _validar_formulario(form):
    descricao = form.get("descricao", "").strip()
    valor = form.get("valor", "")
    tipo = form.get("tipo", "")
    data = form.get("data", "")
    categoria = form.get("categoria", "")

    if not descricao:
        return "Descrição é obrigatória."
    if tipo not in TIPOS_VALIDOS:
        return "Tipo precisa ser receita ou despesa."
    if tipo == "despesa" and categoria not in CATEGORIAS_DESPESA:
        return "Selecione uma categoria válida para a despesa."
    try:
        if float(valor) <= 0:
            return "Valor precisa ser maior que zero."
    except ValueError:
        return "Valor inválido."
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return "Data inválida."
    return None


def _valores_padrao():
    return {"descricao": "", "valor": "", "tipo": "despesa", "data": date.today().isoformat(), "categoria": "Outros"}


def _valores_de_transacao(transacao):
    return {
        "descricao": transacao.descricao,
        "valor": transacao.valor,
        "tipo": transacao.tipo,
        "data": transacao.data.isoformat(),
        "categoria": transacao.categoria or "Outros",
    }


def _valores_de_form(form):
    return {
        "descricao": form.get("descricao", ""),
        "valor": form.get("valor", ""),
        "tipo": form.get("tipo", "despesa"),
        "data": form.get("data", ""),
        "categoria": form.get("categoria", "Outros"),
    }
