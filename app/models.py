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
