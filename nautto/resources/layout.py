import json

from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from nautto.models import User, Widget, Layout
from nautto import db
from nautto.utils import NauttoBuilder, create_error_response
from nautto.constants import *


class LayoutsByUserCollection(Resource):

    def get(self, user):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.layoutsbyusercollection", user=user))
        body.add_control_add_resource('layout', url_for("api.layoutsbyusercollection", user=user))
        body.add_control("nautto:layouts-all", url_for("api.layoutcollection"))
        body["items"] = []
        for db_layout in Layout.query.filter_by(user_id=user):
            item = NauttoBuilder(id=db_layout.id, name=db_layout.name)
            item.add_control("self", url_for("api.layoutitem", layout=db_layout.id))
            item.add_control("profile", LAYOUT_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Layout.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_user = User.query.filter_by(id=user).first()
        if not db_user:
            return create_error_response(
                404, "Not found",
                f'No user was found with the id {user}'
            )

        layout = Layout(
            name=request.json["name"],
            description=request.json["description"],
            user=db_user
        )

        if ('id' in request.json):
            layout.id = request.json["id"]

        try:
            db.session.add(layout)
            db.session.commit()
        except IntegrityError as e:
            return create_error_response(409, "Already exists", str(e))

        db_layout = Layout.query.filter_by(id=layout.id).first()
        headers = {
            "Location": url_for("api.layoutitem", layout=db_layout.id)
        }
        return Response(status=201, headers=headers)


class LayoutCollection(Resource):

    def get(self):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.layoutcollection"))
        body.add_control_add_resource('layout', url_for('api.layoutcollection'))
        body["items"] = []
        for db_layout in Layout.query.all():
            item = NauttoBuilder(id=db_layout.id, name=db_layout.name)
            item.add_control("self", url_for("api.layoutitem", layout=db_layout.id))
            item.add_control("profile", LAYOUT_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)


class LayoutItem(Resource):

    def get(self, layout):
        db_layout = Layout.query.filter_by(id=layout).first()
        if db_layout is None:
            return create_error_response(
                404, "Not found",
                f'No layout was found with the id {layout}'
            )

        body = NauttoBuilder(
            id=db_layout.id,
            name=db_layout.name,
            description=db_layout.description,
        )
        url_for_item = url_for('api.layoutitem', layout=layout)
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for_item)
        body.add_control("profile", LAYOUT_PROFILE)
        body.add_control("collection", url_for("api.layoutcollection"))
        body.add_control("author", url_for("api.useritem", user=db_layout.user_id))
        body.add_control_delete_resource('layout', url_for_item)
        body.add_control_modify_resource('layout', url_for_item)
        body["items"] = []
        for widget in db_layout.widgets:
            item = NauttoBuilder(id=widget.id, name=widget.name)
            item.add_control("self", url_for("api.widgetoflayout", widget=widget.id, layout=layout))
            item.add_control("profile", WIDGET_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, layout):
        db_layout = Layout.query.filter_by(id=layout).first()
        if db_layout is None:
            return create_error_response(
                404, "Not found",
                f'No layout was found with the id {layout}'
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Layout.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if ('id' in request.json):
            db_layout.id = request.json["id"]

        db_layout.name = request.json["name"]
        db_layout.description = request.json["description"]

        if ('items' in request.json):
            for item in request.json['items']:
                widget = Widget.query.filter_by(id=item['id']).first()
                if widget:
                    db_layout.widgets.append(widget)
                else:
                    return create_error_response(
                        404, "Not found",
                        f'No widget was found with id {item["id"]}'
                    )

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Layout with id '{}' already exists.".format(request.json["id"])
            )

        return Response(status=204)

    def delete(self, layout):
        db_layout = Layout.query.filter_by(id=layout).first()
        if db_layout is None:
            return create_error_response(
                404, "Not found",
                f'No layout was found with the id {layout}'
            )

        db.session.delete(db_layout)
        db.session.commit()

        return Response(status=204)


class LayoutOfSet(Resource):

    def get(self, set, layout):
        db_layout = Layout.query.filter_by(id=layout).first()
        if db_layout is None:
            return create_error_response(
                404, "Not found",
                f'No layout was found with the id {layout}'
            )

        body = NauttoBuilder(
            id=db_layout.id,
            name=db_layout.name,
            description=db_layout.description,
        )
        url_for_item = url_for('api.layoutitem', layout=layout)
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for_item)
        body.add_control("profile", LAYOUT_PROFILE)
        body.add_control("collection", url_for("api.layoutcollection"))
        body.add_control("author", url_for("api.useritem", user=db_layout.user_id))
        body.add_control_delete_resource('layout', url_for_item)
        body.add_control_modify_resource('layout', url_for_item)
        body.add_control('up', url_for("api.setitem", set=set))

        return Response(json.dumps(body), 200, mimetype=MASON)