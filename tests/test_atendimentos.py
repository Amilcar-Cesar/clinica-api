import pytest

from src.main.server import create_app
from src.main.repository.database import db
from src.main.models.usuarios_model import Usuarios
from src.main.models.atendimentos_model import Atendimentos


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(username, cargo='user'):
    u = Usuarios(usuario=username, senha='hash', cargo=cargo)
    db.session.add(u)
    db.session.commit()
    return u


def test_create_atendimento_any_user(client):
    user = make_user('u1', 'user')
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True

    payload = {
        'paciente_nome': 'PacienteX',
        'paciente_cpf': '000.111.222-33',
        'especialidade': 'Cardio'

    }
    r = client.post('/atendimentos/', json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data['paciente_nome'] == 'PacienteX'
    assert 'data_hora' in data


def test_list_and_get_atendimento_requires_auth(client):
    # create entry directly (need a user for criado_por_id)
    sys_user = Usuarios(usuario='sys', senha='hash', cargo='admin')
    db.session.add(sys_user)
    db.session.commit()
    a = Atendimentos.from_dict(
        {'paciente_nome': 'P', 'criado_por': 'sys', 'criado_por_id': sys_user.id, 'data_hora': '2025-10-20 10:00'})
    db.session.add(a)
    db.session.commit()

    # no auth
    r = client.get('/atendimentos/')
    assert r.status_code in (401,)

    # with auth
    u = make_user('u2', 'user')
    with client.session_transaction() as sess:
        sess['_user_id'] = str(u.id)
        sess['_fresh'] = True
    r2 = client.get('/atendimentos/')
    assert r2.status_code == 200
    assert isinstance(r2.get_json(), list)


def test_update_delete_admin_only(client):
    admin = make_user('admin', 'admin')
    user = make_user('norm', 'user')
    sys_user = Usuarios(usuario='sys', senha='hash', cargo='admin')
    db.session.add(sys_user)
    db.session.commit()

    a = Atendimentos.from_dict(
        {'paciente_nome': 'Px', 'criado_por': 'sys', 'criado_por_id': sys_user.id, 'data_hora': '2025-10-20 10:00'})
    db.session.add(a)
    db.session.commit()

    # normal cannot update
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    r = client.put(f'/atendimentos/{a.id}', json={'paciente_nome': 'Px2'})
    assert r.status_code in (403, 401)

    # admin can update
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True
    r2 = client.put(f'/atendimentos/{a.id}', json={'paciente_nome': 'Px2'})
    assert r2.status_code == 200
    assert r2.get_json()['paciente_nome'] == 'Px2'

    # admin can delete
    r3 = client.delete(f'/atendimentos/{a.id}')
    assert r3.status_code == 200


def test_list_filters(client):
    # prepare users
    u = Usuarios(usuario='u3', senha='hash', cargo='user')
    db.session.add(u)
    db.session.commit()

    # create atendimentos with different fields
    a1 = Atendimentos.from_dict({'paciente_nome': 'A1', 'paciente_cpf': '111', 'especialidade': 'Cardio',
                                'criado_por': 'sys', 'criado_por_id': u.id, 'data_hora': '2025-10-01 09:00'})
    a2 = Atendimentos.from_dict({'paciente_nome': 'A2', 'paciente_cpf': '222', 'especialidade': 'Dermato',
                                'criado_por': 'sys', 'criado_por_id': u.id, 'data_hora': '2025-11-01 10:00'})
    a3 = Atendimentos.from_dict({'paciente_nome': 'A3', 'paciente_cpf': '111', 'especialidade': 'Cardio',
                                'criado_por': 'sys', 'criado_por_id': u.id, 'data_hora': '2025-12-01 11:00'})
    db.session.add_all([a1, a2, a3])
    db.session.commit()

    # authenticate
    with client.session_transaction() as sess:
        sess['_user_id'] = str(u.id)
        sess['_fresh'] = True

    # filter by paciente_cpf
    r = client.get('/atendimentos/?paciente_cpf=111')
    assert r.status_code == 200
    assert len(r.get_json()) == 2

    # filter by especialidade
    r2 = client.get('/atendimentos/?especialidade=Dermato')
    assert r2.status_code == 200
    assert len(r2.get_json()) == 1

    # filter by date range
    r3 = client.get('/atendimentos/?start=2025-10-15&end=2025-12-31')
    assert r3.status_code == 200
    # should match a2 and a3
    assert len(r3.get_json()) == 2
