from src.main.repository.database import db


class Especialidades(db.Model):
    __tablename__ = 'especialidades'

    id = db.Column(db.Integer, primary_key=True)
    nome_especialidade = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome_especialidade': self.nome_especialidade,
        }

    def __repr__(self):
        return f"<Especialidade id={self.id} nome={self.nome_especialidade}>"

    @classmethod
    def from_dict(cls, data: dict):
        """Criar uma instância de Especialidades a partir de um dict.

        Aceita tanto a chave 'nome_especialidade' quanto 'nome' para conveniência.
        Não faz commit no DB.
        """
        nome = data.get('nome_especialidade') or data.get('nome')
        return cls(nome_especialidade=nome)

    def update_from_dict(self, data: dict):
        """Atualiza campos a partir de um dict.

        Retorna self para encadeamento.
        """
        if 'nome_especialidade' in data and data['nome_especialidade'] is not None:
            self.nome_especialidade = data['nome_especialidade']
        elif 'nome' in data and data['nome'] is not None:
            self.nome_especialidade = data['nome']
        return self
