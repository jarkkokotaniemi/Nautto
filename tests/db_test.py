import os
import pytest
import tempfile
import time

from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from nautto import create_app, db
from nautto.models import User, Widget, Layout, Set


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def app():
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

    yield app

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


def test_create_instances(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    with app.app_context():
        # Create everything
        user = _get_user()
        widget = _get_widget()
        layout = _get_layout()
        sets = _get_set()
        widget.user = user
        layout.user = user
        sets.user = user
        layout.widgets.append(widget)
        sets.layouts.append(layout)
        db.session.add(user)
        db.session.add(widget)
        db.session.add(layout)
        db.session.add(sets)
        db.session.commit()

        # Check that everything exists
        assert User.query.count() == 1
        assert Widget.query.count() == 1
        assert Layout.query.count() == 1
        assert Set.query.count() == 1
        db_user = User.query.first()
        db_widget = Widget.query.first()
        db_layout = Layout.query.first()
        db_set = Set.query.first()

        # Check all relationships (both sides)
        assert db_widget.user == db_user
        assert db_widget in db_layout.widgets
        assert db_layout.user == db_user
        assert db_layout in db_widget.layouts
        assert db_layout in db_set.layouts
        assert db_set.user == db_user
        assert db_set in db_layout.sets


def test_ondelete_user(app):
    """
    Tests that right stuff gets removed when user is deleted
    """

    with app.app_context():
        user = _get_user()
        widget = _get_widget()
        layout = _get_layout()
        sets = _get_set()
        widget.user = user
        layout.user = user
        sets.user = user
        layout.widgets.append(widget)
        sets.layouts.append(layout)
        db.session.add(user)
        db.session.add(widget)
        db.session.add(layout)
        db.session.add(sets)
        db.session.commit()
        assert User.query.count() == 1
        db.session.delete(user)
        assert not User.query.all()
        assert not Widget.query.all()
        assert not Layout.query.all()
        assert not Set.query.all()


def test_ondelete_widget(app):
    """
    Tests that other right stuff gets removed when widget is deleted
    """

    with app.app_context():
        user = _get_user()
        widget = _get_widget()
        layout = _get_layout()
        sets = _get_set()
        widget.user = user
        layout.user = user
        sets.user = user
        layout.widgets.append(widget)
        sets.layouts.append(layout)
        db.session.add(user)
        db.session.add(widget)
        db.session.add(layout)
        db.session.add(sets)
        db.session.commit()
        assert Widget.query.count() == 1
        db.session.delete(widget)
        assert User.query.all()
        assert not Widget.query.all()
        assert Layout.query.all()
        assert Set.query.all()


def test_ondelete_layout(app):
    """
    Tests that other right stuff gets removed when layout is deleted
    """

    with app.app_context():
        user = _get_user()
        widget = _get_widget()
        layout = _get_layout()
        sets = _get_set()
        widget.user = user
        layout.user = user
        sets.user = user
        layout.widgets.append(widget)
        sets.layouts.append(layout)
        db.session.add(user)
        db.session.add(widget)
        db.session.add(layout)
        db.session.add(sets)
        db.session.commit()
        assert Layout.query.count() == 1
        db.session.delete(layout)
        assert User.query.all()
        assert Widget.query.all()
        assert not Layout.query.all()
        assert Set.query.all()


def test_ondelete_set(app):
    """
    Tests that other right stuff gets removed when set is deleted
    """

    with app.app_context():
        user = _get_user()
        widget = _get_widget()
        layout = _get_layout()
        sets = _get_set()
        widget.user = user
        layout.user = user
        sets.user = user
        layout.widgets.append(widget)
        sets.layouts.append(layout)
        db.session.add(user)
        db.session.add(widget)
        db.session.add(layout)
        db.session.add(sets)
        db.session.commit()
        assert Set.query.count() == 1
        db.session.delete(sets)
        assert User.query.all()
        assert Widget.query.all()
        assert Layout.query.all()
        assert not Set.query.all()


def test_user_columns(app):
    """
    Tests user columns' restrictions. Name must be mandatory.
    must be mandatory.
    """

    with app.app_context():
        user = _get_user()
        user.name = None
        db.session.add(user)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


def test_widget_columns(app):
    """
    Tests widget columns' restrictions. Name must be mandatory.
    """

    with app.app_context():
        widget = _get_widget()
        widget.name = None
        db.session.add(widget)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


def test_layout_columns(app):
    """
    Tests layout columns' restrictions. Name must be mandatory.
    """

    with app.app_context():
        layout = _get_layout()
        layout.name = None
        db.session.add(layout)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Tests for column type
        layout = _get_set()
        layout.user_id = time.time()
        db.session.add(layout)
        with pytest.raises(StatementError):
            db.session.commit()


def test_set_columns(app):
    """
    Tests set columns' restrictions. Name must be mandatory.
    """

    with app.app_context():
        set = _get_set()
        set.name = None
        db.session.add(set)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Tests for column type
        set = _get_set()
        set.user_id = time.time()
        db.session.add(set)
        with pytest.raises(StatementError):
            db.session.commit()
