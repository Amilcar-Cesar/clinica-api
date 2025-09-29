from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from src.main.models.usuarios_model import Usuarios


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(hash_pw: str, password: str) -> bool:
    return check_password_hash(hash_pw, password)


def perform_login(user: Usuarios, remember: bool = False):
    login_user(user, remember=remember)


def perform_logout():
    logout_user()


def is_admin() -> bool:
    if not current_user or not hasattr(current_user, 'cargo'):
        return False
    return getattr(current_user, 'cargo') == 'admin'
