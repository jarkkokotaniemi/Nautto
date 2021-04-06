import click

import pytest
import tempfile
import os

from nautto import create_app, db

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
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

def test_db_init(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['db-init'])
    assert 'done' in result.output

def test_db_populate(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['db-populate'])
    assert 'done' in result.output

def test_db_drop(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['db-drop'])
    assert 'done' in result.output