from flask import Blueprint, render_template
from flask_login import login_required
from src.main.models.atendimentos_model import Atendimentos
from src.main.models.pacientes_model import Pacientes
from src.main.models.especialidades_model import Especialidades
from src.main.services.auth import is_admin

home_route_bp = Blueprint("home_route", __name__)


@home_route_bp.route('/', methods=['GET'])
@login_required
def home():
    atendimentos = Atendimentos.query.order_by(Atendimentos.data_hora.desc()).all()
    especialidades = Especialidades.query.order_by(Especialidades.nome_especialidade).all()
    pacientes = Pacientes.query.order_by(Pacientes.nome).all()
    return render_template('home.html',atendimentos=atendimentos, pacientes=pacientes, especialidades=especialidades)