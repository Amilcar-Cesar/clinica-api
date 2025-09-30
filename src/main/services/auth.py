from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import session
from src.main.models.usuarios_model import Usuarios
from src.main.repository.database import db


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(hash_pw: str, password: str) -> bool:
    return check_password_hash(hash_pw, password)


def perform_login(user: Usuarios, remember: bool = False):
    login_user(user, remember=remember)


def perform_logout():
    logout_user()


def is_admin() -> bool:
    """Return True if the current user (or the user id in session) has cargo == 'admin'.

    This supports tests that set session['_user_id'] directly.
    """
    try:
        # First try session id (this supports tests that set it manually)
        uid = session.get('_user_id') or session.get('user_id')
        if uid:
            try:
                u = db.session.get(Usuarios, int(uid))
                if u is not None:
                    return getattr(u, 'cargo', '') == 'admin'
            except Exception:
                pass

        # Fallback to current_user if available
        if getattr(current_user, 'is_authenticated', False):
            return getattr(current_user, 'cargo', '') == 'admin'

        return False
    except Exception:
        return False
