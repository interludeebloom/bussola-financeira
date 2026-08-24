from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .models import Desejo
from .utils import NOMES_MESES

desejos_bp = Blueprint("desejos", __name__, url_prefix="/desejos")


@desejos_bp.route("/")
def listar():
    desejos = Desejo.query.order_by(Desejo.data_meta).all()
    itens = [
        {"desejo": d, "nome_mes_meta": NOMES_MESES[d.data_meta.month]}
        for d in desejos
    ]
    return render_template("desejos.html", itens=itens)


@desejos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro)
            return render_template("form_desejo.html", desejo=None, valores=_valores_de_form(request.form)), 400

        desejo = Desejo(
            nome=request.form["nome"].strip(),
            preco=float(request.form["preco"]),
            data_meta=datetime.strptime(request.form["data_meta"], "%Y-%m-%d").date(),
        )
        db.session.add(desejo)
        db.session.commit()
        return redirect(url_for("desejos.listar"))

    return render_template("form_desejo.html", desejo=None, valores=_valores_padrao())


@desejos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    desejo = Desejo.query.get_or_404(id)

    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro)
            return render_template("form_desejo.html", desejo=desejo, valores=_valores_de_form(request.form)), 400

        desejo.nome = request.form["nome"].strip()
        desejo.preco = float(request.form["preco"])
        desejo.data_meta = datetime.strptime(request.form["data_meta"], "%Y-%m-%d").date()
        db.session.commit()
        return redirect(url_for("desejos.listar"))

    return render_template("form_desejo.html", desejo=desejo, valores=_valores_de_desejo(desejo))


@desejos_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    desejo = Desejo.query.get_or_404(id)
    db.session.delete(desejo)
    db.session.commit()
    return redirect(url_for("desejos.listar"))


@desejos_bp.route("/<int:id>/guardar", methods=["POST"])
def guardar(id):
    desejo = Desejo.query.get_or_404(id)
    valor = request.form.get("valor_guardar", "")
    try:
        valor = float(valor)
    except ValueError:
        valor = 0

    if valor > 0:
        desejo.guardado += valor
        db.session.commit()
    else:
        flash("Informe um valor maior que zero para guardar.")

    return redirect(url_for("desejos.listar"))


def _validar_formulario(form):
    nome = form.get("nome", "").strip()
    preco = form.get("preco", "")
    data_meta = form.get("data_meta", "")

    if not nome:
        return "Nome é obrigatório."
    try:
        if float(preco) <= 0:
            return "Preço precisa ser maior que zero."
    except ValueError:
        return "Preço inválido."
    try:
        datetime.strptime(data_meta, "%Y-%m-%d")
    except ValueError:
        return "Data da meta inválida."
    return None


def _valores_padrao():
    return {"nome": "", "preco": "", "data_meta": ""}


def _valores_de_desejo(desejo):
    return {"nome": desejo.nome, "preco": desejo.preco, "data_meta": desejo.data_meta.isoformat()}


def _valores_de_form(form):
    return {
        "nome": form.get("nome", ""),
        "preco": form.get("preco", ""),
        "data_meta": form.get("data_meta", ""),
    }
