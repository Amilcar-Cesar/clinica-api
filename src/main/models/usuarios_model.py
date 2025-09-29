from flask_login import UserMixin
from src.main.repository.database import db

class Usuarios(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(20), nullable=False, default="admin")