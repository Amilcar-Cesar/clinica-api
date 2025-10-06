from flask import Blueprint, jsonify, request, abort, redirect, url_for,render_template
from flask_login import login_required, current_user
from src.main.repository.database import db
from src.main.models.usuarios_model import Usuarios
from src.main.services.auth import hash_password, verify_password, perform_login, perform_logout, is_admin

usuarios_route_bp = Blueprint("usuarios_route", __name__)


def user_to_dict(user: Usuarios):
    return {
        'id': user.id,
        'usuario': user.usuario,
        'cargo': user.cargo
    }


@usuarios_route_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict() or {}
    usuario = data.get('usuario')
    senha = data.get('senha')
    cargo = data.get('cargo', 'user')

    if not usuario or not senha:
        return jsonify({'error': 'usuario and senha are required'}), 400

    if Usuarios.query.filter_by(usuario=usuario).first():
        return jsonify({'error': 'usuario already exists'}), 400

    new_user = Usuarios(
        usuario=usuario, senha=hash_password(senha), cargo=cargo)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_to_dict(new_user)), 201


@usuarios_route_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if not usuario or not senha:
            return render_template('login.html', error='Usuário e senha são obrigatórios')

        user = Usuarios.query.filter_by(usuario=usuario).first()
        if not user or not verify_password(user.senha, senha):
            return render_template('login.html', error='Credenciais inválidas')

        perform_login(user)

        return render_template('base.html')


    return render_template('login.html')


@usuarios_route_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    perform_logout()
    return jsonify({'message': 'logged out'})


@usuarios_route_bp.route('/', methods=['GET'])
@login_required
def list_users():
    # only admin can list users
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    users = Usuarios.query.all()
    return jsonify([user_to_dict(u) for u in users])


@usuarios_route_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = db.session.get(Usuarios, user_id)
    if user is None:
        abort(404)
    # allow user to see own data or admin
    if current_user.id != user.id and not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    return jsonify(user_to_dict(user))


@usuarios_route_bp.route('/', methods=['POST'])
@login_required
def create_user():
    if not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict() or {}
    usuario = data.get('usuario')
    senha = data.get('senha')
    cargo = data.get('cargo', 'user')
    if not usuario or not senha:
        return jsonify({'error': 'usuario and senha are required'}), 400
    if Usuarios.query.filter_by(usuario=usuario).first():
        return jsonify({'error': 'usuario already exists'}), 400
    new_user = Usuarios(
        usuario=usuario, senha=hash_password(senha), cargo=cargo)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_to_dict(new_user)), 201


@usuarios_route_bp.route('/<int:user_id>', methods=['PUT', 'PATCH'])
@login_required
def update_user(user_id):
    user = db.session.get(Usuarios, user_id)
    if user is None:
        abort(404)
    # only admin or owner can update
    if current_user.id != user.id and not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict() or {}
    usuario = data.get('usuario')
    senha = data.get('senha')
    cargo = data.get('cargo')
    if usuario:
        user.usuario = usuario
    if senha:
        user.senha = hash_password(senha)
    if cargo and is_admin():
        # only admin can change cargo
        user.cargo = cargo
    db.session.commit()
    return jsonify(user_to_dict(user))


@usuarios_route_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = db.session.get(Usuarios, user_id)
    if user is None:
        abort(404)
    if current_user.id != user.id and not is_admin():
        return jsonify({'error': 'forbidden'}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'deleted'})
