import json
import os
import pytest
import tempfile
import time
from datetime import datetime

from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from nautto import create_app, db
from nautto.models import User, Widget, Layout, Set


@pytest.fixture
def client():
    '''
    based on http://flask.pocoo.org/docs/1.0/testing/
    we don't need a client for database testing, just the db handle
    '''
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)


def _get_user(number=1):
    return User(
        name=f'test-user-{number}',
        description=f'test-user-{number}-desc'
    )


def _get_widget(number=1):
    return Widget(
        name=f'test-widget-{number}',
        description=f'test-widget-{number}-desc',
        type="HTML",
        content=f'<p> test <p>'
    )


def _get_layout(number=1):
    return Layout(
        name=f'test-layout-{number}',
        description=f'test-layout-{number}-desc',
    )


def _get_set(number=1):
    return Set(
        name=f'test-set-{number}',
        description=f'test-set-{number}-desc',
    )


def _populate_db():
    # Create everything
    user1 = _get_user(1)
    user2 = _get_user(2)
    widget = _get_widget()
    layout = _get_layout()
    sets = _get_set()
    widget.user = user1
    layout.user = user1
    sets.user = user1
    layout.widgets.append(widget)
    sets.layouts.append(layout)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(widget)
    db.session.add(layout)
    db.session.add(sets)
    db.session.commit()


def _get_user_json(number=1):
    """
    Creates a valid user JSON object to be used for PUT and POST tests.
    """

    return {"name": f'test-user-{number}', "description": f'test-user-{number}-desc'}


def _get_widget_json(number=1):
    """
    Creates a valid widget JSON object to be used for PUT and POST tests.
    """

    return {
        "name": f'test-widget-{number}',
        "description": f'test-widget-{number}-desc',
        "type": "HTML",
        "content": f'<h1> Hello from widget id {number}'
    }


def _check_namespace(client, response):
    """
    Checks that the "nautto" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["nautto"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_put_method(ctrl, client, obj, body):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid user against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


def _check_control_post_method(ctrl, client, obj, body):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid user against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


class TestUserCollection(object):

    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("nautto:add-user", client, body, _get_user_json())
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)

    def test_post(self, client):
        valid = _get_user_json(3)

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "3/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        # send same data again for 409
        valid["id"] = "3"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        valid.pop("id")

        # remove name field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestUserItem(object):

    RESOURCE_URL = "/api/users/1/"
    INVALID_URL = "/api/users/non-user-x/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body, _get_user_json())
        _check_control_delete_method("nautto:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_user_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another user's id
        valid["id"] = "2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test with valid (only change desc)
        valid["id"] = "1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestWidgetsByUserCollection(object):

    USER_ID = 1
    RESOURCE_URL = f'/api/users/{USER_ID}/widgets/'

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("nautto:add-widget", client, body, _get_widget_json())
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)

    def test_post(self, client):
        valid = _get_widget_json(3)

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(f'/api/widgets/2/')
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        # send same data again for 409
        valid["id"] = "2"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        valid.pop("id")

        # remove name field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestWidgetCollection(object):

    RESOURCE_URL = "/api/widgets/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)


class TestWidgetItem(object):

    RESOURCE_URL = "/api/widgets/1/"
    INVALID_URL = "/api/widgets/non-widget-x/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body, _get_widget_json())
        _check_control_delete_method("nautto:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_widget_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another user's id
        valid["id"] = "2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test with valid (only change desc)
        valid["id"] = "1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
