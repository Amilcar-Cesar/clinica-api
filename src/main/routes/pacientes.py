from flask import Blueprint, jsonify, request, abort, render_template, redirect, url_for
from flask_login import login_required
from sqlalchemy import or_
from src.main.repository.database import db
from src.main.models.pacientes_model import Pacientes
from src.main.services.auth import is_admin

pacientes_route_bp = Blueprint("pacientes_route", __name__)


# ROTA PARA LISTAR PACIENTES (GET)
@pacientes_route_bp.route('/', methods=['GET'])
@login_required
def list_pacientes():
    pacientes = Pacientes.query.order_by(Pacientes.nome).all()
    return render_template('pacientes.html', pacientes=pacientes)


# ROTA PARA CRIAR PACIENTE (POST)
@pacientes_route_bp.route('/', methods=['POST'])
@login_required
def create_paciente():
    try:
        paciente = Pacientes.from_dict(request.form.to_dict())
        db.session.add(paciente)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao criar paciente: {e}")
    # Redireciona para a página de onde o usuário veio (ou para a lista como padrão)
    return redirect(request.referrer or url_for('pacientes_route.list_pacientes'))


# ROTA PARA ATUALIZAR PACIENTE (POST)
@pacientes_route_bp.route('/<int:paciente_id>/update', methods=['POST'])
@login_required
def update_paciente(paciente_id):
    paciente = db.session.get(Pacientes, paciente_id)
    if not paciente:
        abort(404)
    try:
        paciente.update_from_dict(request.form.to_dict())
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar paciente: {e}")
    return redirect(request.referrer or url_for('pacientes_route.list_pacientes'))


# ROTA PARA DELETAR PACIENTE (POST)
@pacientes_route_bp.route('/<int:paciente_id>/delete', methods=['POST'])
@login_required
def delete_paciente(paciente_id):
    if not is_admin():
        abort(403)
    paciente = db.session.get(Pacientes, paciente_id)
    if paciente:
        db.session.delete(paciente)
        db.session.commit()
    return redirect(request.referrer or url_for('pacientes_route.list_pacientes'))


# ROTA DE BUSCA (JSON) - SEM ALTERAÇÕES
@pacientes_route_bp.route('/search', methods=['GET'])
@login_required
def search_pacientes():
    query = request.args.get('q', '', type=str)
    if not query:
        return jsonify([])
    pacientes = Pacientes.query.filter(
        or_(Pacientes.nome.ilike(f'%{query}%'), Pacientes.cpf.ilike(f'%{query}%'))
    ).limit(10).all()
    return jsonify([p.to_dict() for p in pacientes])