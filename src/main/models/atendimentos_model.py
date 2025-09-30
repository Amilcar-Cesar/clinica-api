from src.main.repository.database import db
from datetime import datetime


class Atendimentos(db.Model):
    __tablename__ = 'atendimentos'

    id = db.Column(db.Integer, primary_key=True)
    paciente_nome = db.Column(db.String(120), nullable=False)
    paciente_cpf = db.Column(db.String(14), nullable=True)
    # optional FK to Pacientes table; when provided we validate existence and
    # snapshot paciente_nome/paciente_cpf for denormalized read.
    paciente_id = db.Column(db.Integer, db.ForeignKey(
        'pacientes.id'), nullable=True)

    especialidade = db.Column(db.String(120), nullable=True)
    # optional FK to Especialidades
    especialidade_id = db.Column(db.Integer, db.ForeignKey(
        'especialidades.id'), nullable=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    # snapshot of username who created the atendimento
    criado_por = db.Column(db.String(80), nullable=False)
    # FK to Usuarios (id) for stronger relation validation/audit
    criado_por_id = db.Column(
        db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False,
                          server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'paciente_nome': self.paciente_nome,
            'paciente_cpf': self.paciente_cpf,
            'especialidade': self.especialidade,
            'data_hora': self.data_hora.strftime("%d-%m-%Y %H:%M:%S") if self.data_hora else None,
            'criado_por': self.criado_por,
            'criado_em': self.criado_em.strftime("%d-%m-%Y %H:%M:%S") if self.criado_em else None,
        }

    def __repr__(self):
        return f"<Atendimento id={self.id} paciente={self.paciente_nome} especialidade={self.especialidade} data_hora={self.data_hora}>"

    @staticmethod
    def _parse_datetime(value):
        """Parse a datetime from several common formats.

        Accepts datetime objects or strings in formats like:
        - DD-MM-YYYY HH:MM
        - YYYY-MM-DD HH:MM[:SS]
        - ISO 8601
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            s = value.strip()
            # try common formats
            fmts = [
                "%d-%m-%Y %H:%M",
                "%d-%m-%Y %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d",
            ]
            for fmt in fmts:
                try:
                    dt = datetime.strptime(s, fmt)
                    # if only date provided, return date at midnight
                    return dt
                except Exception:
                    continue
            # As a last resort, try fromisoformat
            try:
                return datetime.fromisoformat(s)
            except Exception:
                pass
        raise ValueError(f"Invalid datetime format for data_hora: {value}")

    @classmethod
    def from_dict(cls, data: dict):
        paciente_nome = data.get('paciente_nome') or data.get(
            'nome_paciente') or data.get('nome')
        paciente_cpf = data.get('paciente_cpf') or data.get('cpf')
        especialidade = data.get('especialidade') or data.get(
            'nome_especialidade') or data.get('especialidade_nome')
        data_hora_raw = data.get('data_hora') or data.get(
            'data') or data.get('horario')
        criado_por = data.get('criado_por') or data.get(
            'usuario') or data.get('username')
        paciente_id = data.get('paciente_id')
        especialidade_id = data.get('especialidade_id')
        criado_por_id = data.get('criado_por_id')

        if not paciente_nome:
            raise ValueError('paciente_nome is required')
        if not criado_por and not criado_por_id:
            raise ValueError(
                'criado_por (username) or criado_por_id is required')

        # Validate foreign keys if provided and populate snapshots
        if paciente_id is not None:
            from src.main.models.pacientes_model import Pacientes
            p = db.session.get(Pacientes, int(paciente_id))
            if p is None:
                raise ValueError(f'paciente_id {paciente_id} does not exist')
            paciente_nome = p.nome
            paciente_cpf = p.cpf

        if especialidade_id is not None:
            from src.main.models.especialidades_model import Especialidades
            e = db.session.get(Especialidades, int(especialidade_id))
            if e is None:
                raise ValueError(
                    f'especialidade_id {especialidade_id} does not exist')
            especialidade = e.nome_especialidade

        if criado_por_id is not None:
            from src.main.models.usuarios_model import Usuarios
            u = db.session.get(Usuarios, int(criado_por_id))
            if u is None:
                raise ValueError(
                    f'criado_por_id {criado_por_id} does not exist')
            criado_por = u.usuario

        if data_hora_raw:
            data_hora = cls._parse_datetime(data_hora_raw)
        else:
            # default to now
            data_hora = datetime.now()

        return cls(
            paciente_nome=paciente_nome,
            paciente_cpf=paciente_cpf,
            paciente_id=paciente_id,
            especialidade=especialidade,
            especialidade_id=especialidade_id,
            data_hora=data_hora,
            criado_por=criado_por,
            criado_por_id=criado_por_id,
        )

    def update_from_dict(self, data: dict):
        if 'paciente_nome' in data and data['paciente_nome'] is not None:
            self.paciente_nome = data['paciente_nome']
        if 'paciente_cpf' in data and data['paciente_cpf'] is not None:
            self.paciente_cpf = data['paciente_cpf']
        if 'especialidade' in data and data['especialidade'] is not None:
            self.especialidade = data['especialidade']
        if 'data_hora' in data:
            d = data.get('data_hora')
            if d is None or d == '':
                raise ValueError('data_hora cannot be empty')
            self.data_hora = self._parse_datetime(d)
        if 'criado_por' in data and data['criado_por'] is not None:
            self.criado_por = data['criado_por']
        return self
