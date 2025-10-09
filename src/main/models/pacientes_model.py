from src.main.repository.database import db
from datetime import datetime, date


class Pacientes(db.Model):
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    cartao_sus = db.Column(db.String(30), unique=True, nullable=True)
    endereco = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.strftime("%d-%m-%Y") if self.data_nascimento else None,
            'data_nascimento_form': self.data_nascimento.strftime("%Y-%m-%d") if self.data_nascimento else None,
            'cpf': self.cpf,
            'cartao_sus': self.cartao_sus,
            'endereco': self.endereco,
        }

    def __repr__(self):
        return f"<Paciente id={self.id} nome={self.nome}>"

    @staticmethod
    def _parse_date(value):
        """Parse a date from various formats. Accepts DD-MM-YYYY and YYYY-MM-DD.

        Returns a datetime.date or None.
        """
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            value = value.strip()
            # Try DD-MM-YYYY then ISO
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        # If we can't parse, raise ValueError so caller can handle it
        raise ValueError(f"Invalid date format for data_nascimento: {value}")

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Pacientes instance from a dict, parsing data_nascimento automatically.

        Does not add/commit to the DB.
        """
        nome = data.get('nome')
        dn = data.get('data_nascimento')
        cpf = data.get('cpf')
        cartao_sus = data.get('cartao_sus')
        endereco = data.get('endereco')

        parsed_date = None
        if dn:
            parsed_date = cls._parse_date(dn)

        return cls(nome=nome, data_nascimento=parsed_date, cpf=cpf, cartao_sus=cartao_sus, endereco=endereco)

    def update_from_dict(self, data: dict):
        """Update fields from a dict, parsing date if provided."""
        if 'nome' in data and data['nome'] is not None:
            self.nome = data['nome']
        if 'data_nascimento' in data:
            dn = data.get('data_nascimento')
            if dn is None or dn == '':
                self.data_nascimento = None
            else:
                self.data_nascimento = self._parse_date(dn)
        if 'cpf' in data and data['cpf'] is not None:
            self.cpf = data['cpf']
        if 'cartao_sus' in data and data['cartao_sus'] is not None:
            self.cartao_sus = data['cartao_sus']
        if 'endereco' in data and data['endereco'] is not None:
            self.endereco = data['endereco']
        return self
