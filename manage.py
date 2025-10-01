from src.main.server import create_app
from src.main.repository.database import db

# É crucial importar todos os seus modelos aqui!
# O SQLAlchemy só "vê" os modelos que foram importados em algum lugar.
from src.main.models.usuarios_model import Usuarios
from src.main.models.pacientes_model import Pacientes
from src.main.models.atendimentos_model import Atendimentos
from src.main.models.especialidades_model import Especialidades


# Criamos uma instância da app para ter o "contexto" dela
app = create_app()


def create_tables():
    """
    Função para criar todas as tabelas no banco de dados.
    """
    with app.app_context():
        print("Criando tabelas no banco de dados...")
        db.create_all()
        print("Tabelas criadas com sucesso!")


if __name__ == '__main__':
    create_tables()
