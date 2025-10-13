from src.main.repository.database import db
from datetime import datetime


class Atendimentos(db.Model):
    __tablename__ = 'atendimentos'

    id = db.Column(db.Integer, primary_key=True)
    paciente_nome = db.Column(db.String(120), nullable=False)
    paciente_cpf = db.Column(db.String(14), nullable=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=True)
    especialidade = db.Column(db.String(120), nullable=True)
    especialidade_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=True)
    criado_por = db.Column(db.String(80), nullable=False)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False,server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'paciente_nome': self.paciente_nome,
            'paciente_cpf': self.paciente_cpf,
            'especialidade': self.especialidade,
            'criado_por': self.criado_por,
            'criado_em': self.criado_em.strftime("%d-%m-%Y %H:%M:%S") if self.criado_em else None,
        }

    def __repr__(self):
        return f"<Atendimento id={self.id} paciente={self.paciente_nome} especialidade={self.especialidade}>"

  

    @classmethod
    def from_dict(cls, data: dict):
        # Inicializa variáveis
        paciente_nome = None
        paciente_cpf = None

        paciente_id = data.get('paciente_id')
        especialidade_id = data.get('especialidade_id')
        criado_por_id = data.get('criado_por_id')
        
       
        if paciente_id:
            from src.main.models.pacientes_model import Pacientes
            p = db.session.get(Pacientes, int(paciente_id))
            if p is None:
                raise ValueError(f'Paciente com ID {paciente_id} não existe')
            
            paciente_nome = p.nome
            paciente_cpf = p.cpf
        else:
            paciente_nome = data.get('paciente_nome')

        
        if not paciente_nome:
            raise ValueError('É necessário selecionar um paciente (paciente_id) ou informar um nome (paciente_nome).')
        
        if not criado_por_id:
            raise ValueError('ID do criador do atendimento (criado_por_id) é obrigatório.')

        # Valida especialidade_id e busca nome
        especialidade = data.get('especialidade')
        if especialidade_id:
            from src.main.models.especialidades_model import Especialidades
            e = db.session.get(Especialidades, int(especialidade_id))
            if e is None:
                raise ValueError(f'Especialidade com ID {especialidade_id} não existe')
            especialidade = e.nome_especialidade

        # Valida criado_por_id e busca nome de usuário
        from src.main.models.usuarios_model import Usuarios
        u = db.session.get(Usuarios, int(criado_por_id))
        if u is None:
            raise ValueError(f'Usuário com ID {criado_por_id} não existe')
        criado_por = u.usuario
        
        # Lógica para data_hora
        data_hora_raw = data.get('data_hora')
        if data_hora_raw:
            data_hora = cls._parse_datetime(data_hora_raw)
        else:
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
