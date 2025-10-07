from flask import Flask
from flask_login import LoginManager
from src.main.repository.database import db
import os
from dotenv import load_dotenv
from flask_migrate import Migrate

# Importe suas blueprints aqui
from src.main.routes.usuarios import usuarios_route_bp
from src.main.routes.pacientes import pacientes_route_bp
from src.main.routes.atendimentos import atendimentos_route_bp
from src.main.routes.especialidades import especialidades_route_bp
from src.main.routes.home import home_route_bp

load_dotenv()  # procura .env na árvore de diretórios

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'troque-em-producao')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI') or f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(config=None):
    """
    Função que cria e configura a instância da aplicação Flask.
    Este é o padrão Application Factory.
    """
    app = Flask(__name__, template_folder='../../templates', static_folder='../../static')

    # Carregue configurações (se houver um objeto/config passado, use-o)
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    # --- Inicialização de Extensões ---
    db.init_app(app)

    # --- Flask-Migrate ---
    migrate = Migrate()
    migrate.init_app(app, db)

    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.login_view = 'usuarios_route.login'
    login_manager.init_app(app)

    # For API endpoints return 401 JSON instead of redirecting to a login page
    from flask import jsonify

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return jsonify({'error': 'unauthorized'}), 401

    @login_manager.user_loader
    def load_user(user_id):
        # Import model aqui para evitar import circular
        from src.main.models.usuarios_model import Usuarios
        try:
            return db.session.get(Usuarios, int(user_id))
        except Exception:
            return None

    # Ensure session-based user id (set in tests) is loaded into current_user
    from flask import session
    from flask_login import login_user, current_user

    @app.before_request
    def _load_user_from_session():
        try:
            if not getattr(current_user, 'is_authenticated', False):
                uid = session.get('_user_id') or session.get('user_id')
                if uid:
                    from src.main.models.usuarios_model import Usuarios
                    u = db.session.get(Usuarios, int(uid))
                    if u:
                        # mark user as logged in for this request
                        login_user(u, remember=False)
        except Exception:
            pass

    # --- Registro das Blueprints (Rotas) ---
    app.register_blueprint(usuarios_route_bp, url_prefix='/usuarios')
    app.register_blueprint(pacientes_route_bp, url_prefix='/pacientes')
    app.register_blueprint(atendimentos_route_bp, url_prefix='/atendimentos')
    app.register_blueprint(especialidades_route_bp,
                           url_prefix='/especialidades')
    app.register_blueprint(home_route_bp)

    return app
