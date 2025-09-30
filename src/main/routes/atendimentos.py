from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from src.main.repository.database import db
from src.main.models.atendimentos_model import Atendimentos
from src.main.services.auth import is_admin

atendimentos_route_bp = Blueprint("atendimentos_route", __name__)


def atendimento_to_dict(a: Atendimentos):
    return a.to_dict()


@atendimentos_route_bp.route('/', methods=['POST'])
@login_required
def create_atendimento():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    # ensure criado_por is set to current_user.usuario when available
    if not data.get('criado_por'):
        try:
            data['criado_por'] = current_user.usuario
        except Exception:
            pass
    try:
        atendimento = Atendimentos.from_dict(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    db.session.add(atendimento)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database error', 'detail': str(e)}), 500
    return jsonify(atendimento_to_dict(atendimento)), 201


@atendimentos_route_bp.route('/', methods=['GET'])
@login_required
def list_atendimentos():
    items = Atendimentos.query.all()
    return jsonify([atendimento_to_dict(i) for i in items])


@atendimentos_route_bp.route('/<int:att_id>', methods=['GET'])
@login_required
def get_atendimento(att_id):
    att = db.session.get(Atendimentos, att_id)
    if att is None:
        abort(404)
    return jsonify(atendimento_to_dict(att))


@atendimentos_route_bp.route('/<int:att_id>', methods=['PUT', 'PATCH'])
@login_required
def update_atendimento(att_id):
    # only admin can update
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    att = db.session.get(Atendimentos, att_id)
    if att is None:
        abort(404)
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    try:
        att.update_from_dict(data)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database error', 'detail': str(e)}), 500
    return jsonify(atendimento_to_dict(att))


@atendimentos_route_bp.route('/<int:att_id>', methods=['DELETE'])
@login_required
def delete_atendimento(att_id):
    # only admin can delete
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    att = db.session.get(Atendimentos, att_id)
    if att is None:
        abort(404)
    db.session.delete(att)
    db.session.commit()
    return jsonify({'message': 'deleted'})
