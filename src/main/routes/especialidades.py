from flask import Blueprint, jsonify, request, abort
from flask_login import login_required
from src.main.repository.database import db
from src.main.models.especialidades_model import Especialidades
from src.main.services.auth import is_admin

especialidades_route_bp = Blueprint('especialidades_route', __name__)


def especialidade_to_dict(e: Especialidades):
    return e.to_dict()


@especialidades_route_bp.route('/', methods=['POST'])
@login_required
def create_especialidade():
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    nome = data.get('nome_especialidade') or data.get('nome')
    if not nome:
        return jsonify({'error': 'nome_especialidade is required'}), 400
    new_e = Especialidades.from_dict({'nome_especialidade': nome})
    db.session.add(new_e)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database error', 'detail': str(e)}), 500
    return jsonify(especialidade_to_dict(new_e)), 201


@especialidades_route_bp.route('/', methods=['GET'])
@login_required
def list_especialidades():
    items = Especialidades.query.all()
    return jsonify([especialidade_to_dict(i) for i in items])


@especialidades_route_bp.route('/<int:esp_id>', methods=['GET'])
@login_required
def get_especialidade(esp_id):
    esp = db.session.get(Especialidades, esp_id)
    if esp is None:
        abort(404)
    return jsonify(especialidade_to_dict(esp))


@especialidades_route_bp.route('/<int:esp_id>', methods=['PUT', 'PATCH'])
@login_required
def update_especialidade(esp_id):
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    esp = db.session.get(Especialidades, esp_id)
    if esp is None:
        abort(404)
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    try:
        esp.update_from_dict(data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database error', 'detail': str(e)}), 500
    return jsonify(especialidade_to_dict(esp))


@especialidades_route_bp.route('/<int:esp_id>', methods=['DELETE'])
@login_required
def delete_especialidade(esp_id):
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    esp = db.session.get(Especialidades, esp_id)
    if esp is None:
        abort(404)
    db.session.delete(esp)
    db.session.commit()
    return jsonify({'message': 'deleted'})
