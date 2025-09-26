from flask import Flask
from src.main.repository.database import db

# Importe suas blueprints aqui
from src.main.routes.usuarios import usuarios_route_bp
from src.main.routes.pacientes import pacientes_route_bp
from src.main.routes.atendimentos import atendimentos_route_bp
from src.main.routes.especialidades import especialidades_route_bp

def create_app():
    """
    Função que cria e configura a instância da aplicação Flask.
    Este é o padrão Application Factory.
    """
    app = Flask(__name__)

    # --- Configuração do Banco de Dados ---
    # É uma boa prática mover isso para um arquivo de configuração, mas por enquanto está ok aqui.
    USER = 'admin' # Recomendo usar o usuário da aplicação, não o 'admin'
    PASSWORD = 'adminpassword'
    HOST = '127.0.0.1'
    DATABASE = 'clinica_db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Inicialização de Extensões ---
    db.init_app(app)

    # --- Registro das Blueprints (Rotas) ---
    app.register_blueprint(usuarios_route_bp, url_prefix='/usuarios')
    app.register_blueprint(pacientes_route_bp, url_prefix='/pacientes')
    app.register_blueprint(atendimentos_route_bp, url_prefix='/atendimentos')
    app.register_blueprint(especialidades_route_bp, url_prefix='/especialidades')
    
    return app