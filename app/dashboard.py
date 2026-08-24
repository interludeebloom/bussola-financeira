from calendar import monthrange
from datetime import date

from flask import Blueprint, jsonify

from .models import Banco, Desejo, Fatura, Transacao
from .utils import NOMES_MESES

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/")
def index():
    hoje = date.today()
    ano, mes = hoje.year, hoje.month
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])

    transacoes_mes = Transacao.query.filter(
        Transacao.data >= primeiro_dia, Transacao.data <= ultimo_dia
    ).all()
    total_receitas = sum(t.valor for t in transacoes_mes if t.tipo == "receita")
    total_despesas = sum(t.valor for t in transacoes_mes if t.tipo == "despesa")

    totais_por_categoria = {}
    for t in transacoes_mes:
        if t.tipo != "despesa":
            continue
        categoria = t.categoria or "Outros"
        totais_por_categoria[categoria] = totais_por_categoria.get(categoria, 0.0) + t.valor
    despesas_por_categoria = sorted(totais_por_categoria.items(), key=lambda item: item[1], reverse=True)

    desejos = Desejo.query.order_by(Desejo.data_meta).all()

    faturas_mes = []
    total_faturas_aberto = 0.0
    for banco in Banco.query.order_by(Banco.nome).all():
        fatura = Fatura.query.filter_by(banco_id=banco.id, ano=ano, mes=mes).first()
        total = fatura.total if fatura else 0.0
        total_faturas_aberto += total
        faturas_mes.append({"banco": banco.nome, "total": total})

    return jsonify({
        "nome_mes": NOMES_MESES[mes],
        "ano": ano,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo_mes": total_receitas - total_despesas,
        "desejos": [d.to_dict() for d in desejos],
        "faturas_mes": faturas_mes,
        "total_faturas_aberto": total_faturas_aberto,
        "despesas_por_categoria": [{"categoria": c, "total": t} for c, t in despesas_por_categoria],
    })
