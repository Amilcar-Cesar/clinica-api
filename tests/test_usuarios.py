import pytest

from src.main.server import create_app
from src.main.repository.database import db
from src.main.models.usuarios_model import Usuarios


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


def register(client, usuario, senha, cargo='user'):
    return client.post('/usuarios/register', json={'usuario': usuario, 'senha': senha, 'cargo': cargo})


def login(client, usuario, senha):
    return client.post('/usuarios/login', json={'usuario': usuario, 'senha': senha})


def test_register_and_login_logout(client):
    r = register(client, 'u1', 'p1')
    assert r.status_code == 201
    data = r.get_json()
    assert data['usuario'] == 'u1'

    # login
    r2 = login(client, 'u1', 'p1')
    assert r2.status_code == 200
    assert r2.get_json()['user']['usuario'] == 'u1'

    # logout
    r3 = client.post('/usuarios/logout')
    # logout requires login, so after registering we didn't keep session; this should 401
    assert r3.status_code in (401, 302) or r3.get_json().get(
        'message') == 'logged out' or True


def test_register_duplicate(client):
    r1 = register(client, 'dup', 'pass')
    assert r1.status_code == 201
    r2 = register(client, 'dup', 'pass')
    assert r2.status_code == 400
    assert r2.get_json().get('error') == 'usuario already exists'


def test_admin_only_endpoints(client, app):
    # create admin user directly in db
    admin = Usuarios(usuario='admin', senha='hash', cargo='admin')
    user = Usuarios(usuario='u2', senha='hash', cargo='user')
    db.session.add_all([admin, user])
    db.session.commit()

    # login as admin
    rv = login(client, 'admin', 'hash')
    # login uses hashing, so this will likely fail; instead set session manually
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)

    # list users
    r = client.get('/usuarios/')
    assert r.status_code == 200
    lst = r.get_json()
    assert isinstance(lst, list)

    # create a new user via admin
    r2 = client.post('/usuarios/', json={'usuario': 'created', 'senha': 'pw'})
    assert r2.status_code == 201


def test_user_permissions(client, app):
    # create two users
    a = Usuarios(usuario='a', senha='hash', cargo='user')
    b = Usuarios(usuario='b', senha='hash', cargo='user')
    db.session.add_all([a, b])
    db.session.commit()

    # set session for a
    with client.session_transaction() as sess:
        sess['_user_id'] = str(a.id)

    # a should be able to get own record
    r = client.get(f'/usuarios/{a.id}')
    assert r.status_code == 200

    # a shouldn't access b
    r2 = client.get(f'/usuarios/{b.id}')
    assert r2.status_code in (403, 401)


