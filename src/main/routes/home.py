from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.main.repository.database import db
from src.main.models.atendimentos_model import Atendimentos
from src.main.services.auth import is_admin

home_route_bp = Blueprint("home_route", __name__)


@home_route_bp.route('/', methods=['GET'])
@login_required
def home():
    return render_template('base.html')