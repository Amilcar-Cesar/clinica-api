import pytest

from src.main.server import create_app
from src.main.repository.database import db
from src.main.models.usuarios_model import Usuarios
from src.main.models.pacientes_model import Pacientes


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


def test_create_paciente_as_authenticated_user(client):
    user = make_user('u1', 'user')
    # simulate login
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True

    payload = {
        'nome': 'Paciente 1',
        'data_nascimento': '15-08-1990',
        'cpf': '123.456.789-00',
        'cartao_sus': 'SUS123',
        'endereco': 'Rua A, 123'
    }
    r = client.post('/pacientes/', json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data['nome'] == 'Paciente 1'
    assert data['data_nascimento'] == '1990-08-15'


def test_update_paciente_as_authenticated_user(client):
    user = make_user('u2', 'user')
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True

    # create paciente
    p = Pacientes.from_dict(
        {'nome': 'P2', 'data_nascimento': '1990-01-01', 'cpf': '111', 'cartao_sus': 'S1'})
    db.session.add(p)
    db.session.commit()

    # update date using DD-MM-YYYY
    r = client.put(
        f'/pacientes/{p.id}', json={'data_nascimento': '20-12-1985', 'endereco': 'Nova Rua'})
    assert r.status_code == 200
    data = r.get_json()
    assert data['data_nascimento'] == '1985-12-20'
    assert data['endereco'] == 'Nova Rua'


def test_list_and_delete_requires_admin(client):
    admin = make_user('admin', 'admin')
    u = make_user('normal', 'user')

    # create a paciente
    p = Pacientes.from_dict(
        {'nome': 'P3', 'data_nascimento': '01-01-2000', 'cpf': '222'})
    db.session.add(p)
    db.session.commit()

    # any authenticated user can list
    with client.session_transaction() as sess:
        sess['_user_id'] = str(u.id)
        sess['_fresh'] = True
    r = client.get('/pacientes/')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

    # admin can also list and delete
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True
    r2 = client.get('/pacientes/')
    assert r2.status_code == 200
    assert isinstance(r2.get_json(), list)

    # admin can delete
    r3 = client.delete(f'/pacientes/{p.id}')
    assert r3.status_code == 200


def test_get_paciente_requires_auth(client):
    p = Pacientes.from_dict({'nome': 'P4'})
    db.session.add(p)
    db.session.commit()

    # no auth
    r = client.get(f'/pacientes/{p.id}')
    assert r.status_code in (401,)

    # with auth
    user = make_user('userx', 'user')
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    r2 = client.get(f'/pacientes/{p.id}')
    assert r2.status_code == 200
