from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from src.main.repository.database import db
from src.main.models.atendimentos_model import Atendimentos
from src.main.services.auth import is_admin

atendimentos_route_bp = Blueprint("atendimentos_route", __name__)


def atendimento_to_dict(a: Atendimentos):
    d = a.to_dict()
    # include FK ids if available
    if hasattr(a, 'paciente_id'):
        d['paciente_id'] = a.paciente_id
    if hasattr(a, 'especialidade_id'):
        d['especialidade_id'] = a.especialidade_id
    if hasattr(a, 'criado_por_id'):
        d['criado_por_id'] = a.criado_por_id
    return d


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
    # also set criado_por_id to current_user.id when available
    if not data.get('criado_por_id'):
        try:
            data['criado_por_id'] = getattr(current_user, 'id', None)
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
    # Filters via query params
    q = Atendimentos.query
    paciente_id = request.args.get('paciente_id')
    paciente_cpf = request.args.get('paciente_cpf')
    especialidade_id = request.args.get('especialidade_id')
    especialidade = request.args.get('especialidade')
    start = request.args.get('start')
    end = request.args.get('end')

    if paciente_id:
        try:
            q = q.filter(Atendimentos.paciente_id == int(paciente_id))
        except ValueError:
            return jsonify({'error': 'invalid paciente_id'}), 400
    if paciente_cpf:
        q = q.filter(Atendimentos.paciente_cpf == paciente_cpf)
    if especialidade_id:
        try:
            q = q.filter(Atendimentos.especialidade_id ==
                         int(especialidade_id))
        except ValueError:
            return jsonify({'error': 'invalid especialidade_id'}), 400
    if especialidade:
        q = q.filter(Atendimentos.especialidade.ilike(f"%{especialidade}%"))

    # date range filtering (start/end are parsed using model helper)
    if start:
        try:
            sdt = Atendimentos._parse_datetime(start)
            q = q.filter(Atendimentos.data_hora >= sdt)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    if end:
        try:
            edt = Atendimentos._parse_datetime(end)
            q = q.filter(Atendimentos.data_hora <= edt)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    items = q.all()
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
