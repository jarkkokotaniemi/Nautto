import os
import json

from flask import Flask, Response, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event

from nautto.utils import NauttoBuilder
from nautto.constants import *

db = SQLAlchemy()


def create_app(test_config=None):
    '''
    Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
    Modified to use Flask SQLAlchemy
    '''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" +
        os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # Force foreing key usage
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from . import models
    app.cli.add_command(models.db_init_cmd)
    app.cli.add_command(models.db_drop_cmd)
    app.cli.add_command(models.db_populate_cmd)

    from . import api
    app.register_blueprint(api.api_bp)

    @app.route("/")
    def index():
        return "Go to /api/ for api entrypoint OR to /admin/ for admin client"

    @app.route("/admin/")
    def admin_site():
        return app.send_static_file("html/admin.html")

    @app.route("/api/")
    def api_index():
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("entrypoint", url_for("api.usercollection"))
        return Response(json.dumps(body), 200, mimetype=MASON)

    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return "link relations"

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        return "you requests {} profile".format(profile)

    return app
