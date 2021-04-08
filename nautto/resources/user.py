import json

from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from nautto.models import User
from nautto import db
from nautto.utils import NauttoBuilder, create_error_response
from nautto.constants import *


class UserCollection(Resource):

    def get(self):
        body = NauttoBuilder()
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.usercollection"))
        body.add_control_add_resource('user', url_for('api.usercollection'))
        body["items"] = []
        for db_user in User.query.all():
            item = NauttoBuilder(id=db_user.id, name=db_user.name)
            item.add_control("self", url_for("api.useritem", user=db_user.id))
            item.add_control("profile", USER_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, User.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        user = User(
            name=request.json["name"],
            description=request.json["description"],
        )

        if ('id' in request.json):
            user.id = request.json["id"]

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "User with id '{}' already exists.".format(
                    request.json["id"])
            )

        db_user = User.query.filter_by(id=user.id).first()
        headers = {
            "Location": url_for("api.useritem", user=db_user.id)
        }
        return Response(status=201, headers=headers)


class UserItem(Resource):

    def get(self, user):
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                404, "Not found",
                f'No user was found with the id {user}'
            )
        
        body = NauttoBuilder(
            id=db_user.id,
            name=db_user.name,
            description=db_user.description,
        )
        url_for_item = url_for('api.useritem', user=user)
        body.add_namespace("nautto", LINK_RELATIONS_URL)
        body.add_control("self", url_for_item)
        body.add_control("profile", USER_PROFILE)
        body.add_control("collection", url_for("api.usercollection"))
        body.add_control("nautto:widgets-by", url_for("api.widgetcollection"))
        #body.add_control("nautto:layouts-by", url_for("api.layoutcollection"))
        #body.add_control("nautto:sets-by", url_for("api.setcollection"))
        body.add_control_delete_resource('user', url_for_item)
        body.add_control_modify_resource('user', url_for_item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user):
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                404, "Not found",
                f'No user was found with the id {user}'
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, User.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if ('id' in request.json):
            db_user.id = request.json["id"]

        db_user.name = request.json["name"]
        db_user.description = request.json["description"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "User with id '{}' already exists.".format(
                    request.json["id"])
            )

        return Response(status=204)

    def delete(self, user):
        db_user = User.query.filter_by(id=user).first()
        if db_user is None:
            return create_error_response(
                404, "Not found",
                f'No user was found with the id {user}'
            )

        db.session.delete(db_user)
        db.session.commit()

        return Response(status=204)
