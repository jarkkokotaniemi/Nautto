import json

from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from nautto.models import Widget, User
from nautto import db
from nautto.utils import NauttoBuilder, create_error_response
from nautto.constants import *


class WidgetsByUserCollection(Resource):

    def get(self, user):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.widgetsbyusercollection", user=user))
        body.add_control_add_resource('widget', url_for("api.widgetsbyusercollection", user=user))
        body.add_control("author", url_for("api.useritem", user=user))
        body.add_control("nautto:widgets-all", url_for("api.widgetcollection"))
        body["items"] = []
        for db_widget in Widget.query.filter_by(user_id=user):
            item = NauttoBuilder(id=db_widget.id, name=db_widget.name)
            item.add_control("self", url_for(
                "api.widgetitem", widget=db_widget.id))
            item.add_control("profile", WIDGET_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Widget.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_user = User.query.filter_by(id=user).first()
        if not db_user:
            return create_error_response(
                404, "Not found",
                f'No user was found with the id {user}'
            )

        widget = Widget(
            name=request.json["name"],
            type=request.json["type"],
            content=request.json["content"],
            user=db_user
        )

        if ('description' in request.json):
            widget.description = request.json["description"]

        if ('id' in request.json):
            widget.id = request.json["id"]

        try:
            db.session.add(widget)
            db.session.commit()
        except IntegrityError as e:
            return create_error_response(409, "Already exists", str(e))

        db_widget = Widget.query.filter_by(id=widget.id).first()
        headers = {
            "Location": url_for("api.widgetitem", widget=db_widget.id)
        }
        return Response(status=201, headers=headers)


class WidgetCollection(Resource):

    def get(self):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.widgetcollection"))
        body.add_control_add_resource('widget', url_for('api.widgetcollection'))
        body["items"] = []
        for db_widget in Widget.query.all():
            item = NauttoBuilder(id=db_widget.id, name=db_widget.name)
            item.add_control("self", url_for("api.widgetitem", widget=db_widget.id))
            item.add_control("profile", WIDGET_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)


class WidgetItem(Resource):

    def get(self, widget):
        db_widget = Widget.query.filter_by(id=widget).first()
        if db_widget is None:
            return create_error_response(
                404, "Not found",
                f'No widget was found with the id {widget}'
            )

        body = NauttoBuilder(
            id=db_widget.id,
            name=db_widget.name,
            description=db_widget.description,
            type=db_widget.type,
            content=db_widget.content,
        )
        url_for_item = url_for('api.widgetitem', widget=widget)
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for_item)
        body.add_control("profile", WIDGET_PROFILE)
        body.add_control("collection", url_for("api.widgetcollection"))
        body.add_control("author", url_for("api.useritem", user=db_widget.user_id))
        body.add_control_delete_resource('widget', url_for_item)
        body.add_control_modify_resource('widget', url_for_item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, widget):
        db_widget = Widget.query.filter_by(id=widget).first()
        if db_widget is None:
            return create_error_response(
                404, "Not found",
                f'No widget was found with the id {widget}'
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Widget.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if ('id' in request.json):
            db_widget.id = request.json["id"]

        db_widget.name = request.json["name"]
        db_widget.type = request.json["type"]
        db_widget.content = request.json["content"]
        
        if ('description' in request.json):
            db_widget.description = request.json["description"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Widget with id '{}' already exists.".format(request.json["id"])
            )

        return Response(status=204)

    def delete(self, widget):
        db_widget = Widget.query.filter_by(id=widget).first()
        if db_widget is None:
            return create_error_response(
                404, "Not found",
                f'No widget was found with the id {widget}'
            )

        db.session.delete(db_widget)
        db.session.commit()

        return Response(status=204)


class WidgetOfLayout(Resource):

    def get(self, layout, widget):
        db_widget = Widget.query.filter_by(id=widget).first()
        if db_widget is None:
            return create_error_response(
                404, "Not found",
                f'No widget was found with the id {widget}'
            )

        body = NauttoBuilder(
            id=db_widget.id,
            name=db_widget.name,
            description=db_widget.description,
            type=db_widget.type,
            content=db_widget.content,
        )
        url_for_item = url_for('api.widgetitem', widget=widget)
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for_item)
        body.add_control("profile", WIDGET_PROFILE)
        body.add_control("collection", url_for("api.widgetcollection"))
        body.add_control("author", url_for("api.useritem", user=db_widget.user_id))
        body.add_control_delete_resource('widget', url_for_item)
        body.add_control_modify_resource('widget', url_for_item)
        body.add_control('up', url_for("api.layoutitem", layout=layout))

        return Response(json.dumps(body), 200, mimetype=MASON)