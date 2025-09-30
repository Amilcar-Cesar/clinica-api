import pytest

from src.main.server import create_app
from src.main.repository.database import db
from src.main.models.usuarios_model import Usuarios
from src.main.models.especialidades_model import Especialidades


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


def test_create_especialidade_admin_only(client):
    admin = make_user('admin', 'admin')
    user = make_user('normal', 'user')

    # normal user cannot create
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    r = client.post('/especialidades/', json={'nome_especialidade': 'Cardio'})
    assert r.status_code in (403, 401)

    # admin can create
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True
    r2 = client.post('/especialidades/', json={'nome_especialidade': 'Cardio'})
    assert r2.status_code == 201
    data = r2.get_json()
    assert data['nome_especialidade'] == 'Cardio'

    # create without name -> 400
    r3 = client.post('/especialidades/', json={})
    assert r3.status_code == 400


def test_list_and_get_requires_auth(client):
    # create some entries directly
    e1 = Especialidades(nome_especialidade='Dermato')
    e2 = Especialidades(nome_especialidade='Pediatria')
    db.session.add_all([e1, e2])
    db.session.commit()

    # no auth -> 401
    r = client.get('/especialidades/')
    assert r.status_code in (401,)

    # with auth any user can list and get
    user = make_user('u1', 'user')
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    r2 = client.get('/especialidades/')
    assert r2.status_code == 200
    lst = r2.get_json()
    assert isinstance(lst, list)

    # get by id
    r3 = client.get(f'/especialidades/{e1.id}')
    assert r3.status_code == 200
    assert r3.get_json()['nome_especialidade'] == 'Dermato'


def test_update_and_delete_admin_only(client):
    admin = make_user('admin2', 'admin')
    user = make_user('normal2', 'user')

    e = Especialidades(nome_especialidade='Ortopedia')
    db.session.add(e)
    db.session.commit()

    # normal user cannot update
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    r = client.put(f'/especialidades/{e.id}',
                   json={'nome_especialidade': 'Orto'})
    assert r.status_code in (403, 401)

    # admin can update
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True
    r2 = client.put(f'/especialidades/{e.id}',
                    json={'nome_especialidade': 'Orto'})
    assert r2.status_code == 200
    assert r2.get_json()['nome_especialidade'] == 'Orto'

    # admin can delete
    r3 = client.delete(f'/especialidades/{e.id}')
    assert r3.status_code == 200

    # ensure deleted
    r4 = client.get(f'/especialidades/{e.id}')
    assert r4.status_code in (404,)
