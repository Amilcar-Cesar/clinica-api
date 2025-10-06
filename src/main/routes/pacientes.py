from flask import Blueprint, jsonify, request, abort, render_template
from flask_login import login_required, current_user
from src.main.repository.database import db
from src.main.models.pacientes_model import Pacientes
from src.main.models.usuarios_model import Usuarios
from src.main.services.auth import is_admin

pacientes_route_bp = Blueprint("pacientes_route", __name__)


def paciente_to_dict(p: Pacientes):
    return p.to_dict()


@pacientes_route_bp.route('/', methods=['POST', 'GET'])
@login_required
def create_paciente():
    if request.method == 'POST': 
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        try:
            paciente = Pacientes.from_dict(data)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        db.session.add(paciente)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'database error', 'detail': str(e)}), 500
        return jsonify(paciente_to_dict(paciente)), 201
    return render_template('exemplo_form.html')

@pacientes_route_bp.route('/<int:paciente_id>', methods=['GET'])
@login_required
def get_paciente(paciente_id):
    paciente = db.session.get(Pacientes, paciente_id)
    if paciente is None:
        abort(404)
    return jsonify(paciente_to_dict(paciente))


@pacientes_route_bp.route('/<int:paciente_id>', methods=['PUT', 'PATCH'])
@login_required
def update_paciente(paciente_id):
    paciente = db.session.get(Pacientes, paciente_id)
    if paciente is None:
        abort(404)
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    try:
        paciente.update_from_dict(data)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database error', 'detail': str(e)}), 500
    return jsonify(paciente_to_dict(paciente))


@pacientes_route_bp.route('/', methods=['GET'])
@login_required
def list_pacientes():
    pacs = Pacientes.query.all()
    return jsonify([paciente_to_dict(p) for p in pacs])


@pacientes_route_bp.route('/<int:paciente_id>', methods=['DELETE'])
@login_required
def delete_paciente(paciente_id):
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    paciente = db.session.get(Pacientes, paciente_id)
    if paciente is None:
        abort(404)
    db.session.delete(paciente)
    db.session.commit()
    return jsonify({'message': 'deleted'})
