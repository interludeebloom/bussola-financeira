from datetime import date

from . import db


class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(8), nullable=False)  # "receita" ou "despesa"
    data = db.Column(db.Date, nullable=False, default=date.today)

    @property
    def valor_com_sinal(self):
        return self.valor if self.tipo == "receita" else -self.valor


class GastoFixo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=False)  # 1 a 31
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    pagamentos = db.relationship(
        "PagamentoFixo", backref="gasto_fixo", cascade="all, delete-orphan"
    )

    def pagamento_do_mes(self, ano, mes):
        return PagamentoFixo.query.filter_by(
            gasto_fixo_id=self.id, ano=ano, mes=mes
        ).first()


class PagamentoFixo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gasto_fixo_id = db.Column(db.Integer, db.ForeignKey("gasto_fixo.id"), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1 a 12
    pago = db.Column(db.Boolean, nullable=False, default=False)
    data_pagamento = db.Column(db.Date, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("gasto_fixo_id", "ano", "mes", name="uq_pagamento_fixo_mes"),
    )
