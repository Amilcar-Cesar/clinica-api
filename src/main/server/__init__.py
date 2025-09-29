from flask import Flask
from flask_login import LoginManager
from src.main.repository.database import db
import os
from dotenv import load_dotenv

# Importe suas blueprints aqui
from src.main.routes.usuarios import usuarios_route_bp
from src.main.routes.pacientes import pacientes_route_bp
from src.main.routes.atendimentos import atendimentos_route_bp
from src.main.routes.especialidades import especialidades_route_bp


load_dotenv()  # procura .env na árvore de diretórios

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'troque-em-producao')
    # Ajuste o driver: mysql+pymysql ou mysql+mysqlconnector conforme seu driver instalado
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI') or f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(config=None):
    """
    Função que cria e configura a instância da aplicação Flask.
    Este é o padrão Application Factory.
    """
    app = Flask(__name__)

    # Carregue configurações (se houver um objeto/config passado, use-o)
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    # --- Configuração do Banco de Dados (fallback simples) ---
    # Se as configurações específicas não estiverem definidas, usa valores de desenvolvimento.
    app.config.setdefault('SQLALCHEMY_DATABASE_URI',
                          'sqlite:///clinica_dev.db')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # --- Inicialização de Extensões ---
    db.init_app(app)

    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.login_view = 'usuarios_route.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Import model aqui para evitar import circular
        from src.main.models.usuarios_model import Usuarios
        try:
            return db.session.get(Usuarios, int(user_id))
        except Exception:
            return None

    # --- Registro das Blueprints (Rotas) ---
    app.register_blueprint(usuarios_route_bp, url_prefix='/usuarios')
    app.register_blueprint(pacientes_route_bp, url_prefix='/pacientes')
    app.register_blueprint(atendimentos_route_bp, url_prefix='/atendimentos')
    app.register_blueprint(especialidades_route_bp,
                           url_prefix='/especialidades')

    return app
