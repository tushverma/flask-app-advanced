from typing import Dict, List
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    fresh_jwt_required,
)
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

class Item(Resource):

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": "Item not found."}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return (
                {"message": "An item with name '{}' already exists.".format(name)},
                400,
            )

        data = request.get_json()
        data["name"] = name
        item = item_schema.load(**data)
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred while inserting the item."}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "Item deleted."}, 200
        return {"message": "Item not found."}, 404

    @classmethod
    def put(cls, name: str):
        data = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            data["name"] = name
            item = item_schema.load(**data)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
