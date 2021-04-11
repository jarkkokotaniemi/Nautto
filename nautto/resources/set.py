import json

from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from nautto.models import Set, User, Layout
from nautto import db
from nautto.utils import NauttoBuilder, create_error_response
from nautto.constants import *


class SetsByUserCollection(Resource):

    def get(self, user):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.setsbyusercollection", user=user))
        body.add_control_add_resource('set', url_for("api.setsbyusercollection", user=user))
        body.add_control("nautto:sets-all", url_for("api.setcollection"))
        body["items"] = []
        for db_set in Set.query.filter_by(user_id=user):
            item = NauttoBuilder(id=db_set.id, name=db_set.name)
            item.add_control("self", url_for("api.setitem", set=db_set.id))
            item.add_control("profile", SET_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Set.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_user = User.query.filter_by(id=user).first()
        if not db_user:
            return create_error_response(
                404, "Not found",
                f'No user was found with the id {user}'
            )

        set = Set(
            name=request.json["name"],
            description=request.json["description"],
            user=db_user
        )

        if ('id' in request.json):
            set.id = request.json["id"]

        try:
            db.session.add(set)
            db.session.commit()
        except IntegrityError as e:
            return create_error_response(409, "Already exists", str(e))

        db_set = Set.query.filter_by(id=set.id).first()
        headers = {
            "Location": url_for("api.setitem", set=db_set.id)
        }
        return Response(status=201, headers=headers)


class SetCollection(Resource):

    def get(self):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.setcollection"))
        body.add_control_add_resource('set', url_for('api.setcollection'))
        body["items"] = []
        for db_set in Set.query.all():
            item = NauttoBuilder(id=db_set.id, name=db_set.name)
            item.add_control("self", url_for("api.setitem", set=db_set.id))
            item.add_control("profile", SET_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)


class SetItem(Resource):

    def get(self, set):
        db_set = Set.query.filter_by(id=set).first()
        if db_set is None:
            return create_error_response(
                404, "Not found",
                f'No set was found with the id {set}'
            )

        body = NauttoBuilder(
            id=db_set.id,
            name=db_set.name,
            description=db_set.description,
        )
        url_for_item = url_for('api.setitem', set=set)
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for_item)
        body.add_control("profile", SET_PROFILE)
        body.add_control("collection", url_for("api.setcollection"))
        body.add_control("author", url_for("api.useritem", user=db_set.user_id))
        body.add_control_delete_resource('set', url_for_item)
        body.add_control_modify_resource('set', url_for_item)
        body["items"] = []
        for layout in db_set.layouts:
            item = NauttoBuilder(id=layout.id, name=layout.name)
            item.add_control("self", url_for("api.layoutitem", layout=layout.id))
            item.add_control("profile", LAYOUT_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, set):
        db_set = Set.query.filter_by(id=set).first()
        if db_set is None:
            return create_error_response(
                404, "Not found",
                f'No set was found with the id {set}'
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Set.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if ('id' in request.json):
            db_set.id = request.json["id"]

        db_set.name = request.json["name"]
        db_set.description = request.json["description"]

        if ('items' in request.json):
            for item in request.json['items']:
                layout = Layout.query.filter_by(id=item['id']).first()
                if layout:
                    db_set.layouts.append(layout)
                else:
                    return create_error_response(
                        404, "Not found",
                        f'No layout was found with id {item["id"]}'
                    )


        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Set with id '{}' already exists.".format(request.json["id"])
            )

        return Response(status=204)

    def delete(self, set):
        db_set = Set.query.filter_by(id=set).first()
        if db_set is None:
            return create_error_response(
                404, "Not found",
                f'No set was found with the id {set}'
            )

        db.session.delete(db_set)
        db.session.commit()

        return Response(status=204)
