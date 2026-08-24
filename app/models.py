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


class Desejo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    guardado = db.Column(db.Float, nullable=False, default=0.0)
    data_meta = db.Column(db.Date, nullable=False)

    @property
    def falta(self):
        return max(0.0, self.preco - self.guardado)

    @property
    def meta_atingida(self):
        return self.guardado >= self.preco

    @property
    def progresso_pct(self):
        if self.preco <= 0:
            return 0
        return min(100, round(self.guardado / self.preco * 100))

    @property
    def meses_restantes(self):
        """Meses inteiros entre hoje e data_meta, contando o mês atual. Mínimo 1."""
        hoje = date.today()
        meses = (self.data_meta.year - hoje.year) * 12 + (self.data_meta.month - hoje.month) + 1
        return max(1, meses)

    @property
    def valor_mensal(self):
        if self.meta_atingida:
            return 0.0
        return self.falta / self.meses_restantes


class Banco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)

    faturas = db.relationship("Fatura", backref="banco", cascade="all, delete-orphan")


class Fatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    banco_id = db.Column(db.Integer, db.ForeignKey("banco.id"), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1 a 12

    gastos = db.relationship(
        "GastoFatura", backref="fatura", cascade="all, delete-orphan", order_by="GastoFatura.data"
    )

    __table_args__ = (
        db.UniqueConstraint("banco_id", "ano", "mes", name="uq_fatura_banco_mes"),
    )

    @property
    def total(self):
        return sum(g.valor for g in self.gastos)


class GastoFatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fatura_id = db.Column(db.Integer, db.ForeignKey("fatura.id"), nullable=False)
    descricao = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=True)
