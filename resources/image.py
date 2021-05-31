import os

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
from libs import image_helper
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        """
        Used to upload an Image file
        It use JWT to get user information and saves the image to the user's folder
        If these is a filename conflict it appends a number at the end.
        """
        data = image_schema.load(request.files)  # {'image': FileStorage}
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"  # static/images/user_1
        try:
            image_path = image_helper.save_image(data['image'], folder)
            basename = image_helper.get_basename(image_path)
            return {"message": f"{basename} Image uploaded successfully"}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data['image'])
            return {"message": f"{extension}Extension not allowed"}, 400
        except:
            return {"message": "Server Error"}, 500


class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "Illegal file name"}, 400
        try:
            return send_file(image_helper.get_path(filename, folder))
        except FileNotFoundError:
            return {"message": "Image Not found"}, 404
    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "Illegal file name"}, 400
        try:
            os.remove(image_helper.get_path(filename, folder))
            return {"message": "Image deleted"}, 200
        except FileNotFoundError:
            return {"message": " File not found"}, 404
        except:
            traceback.print_exc()
            return {"message": "Delete image failed"}, 500


class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": "Avatar delete failed"}, 500
        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(data['image'], folder, avatar)
            basename = image_helper.get_basename(avatar_path)
            return {"message": f"{basename} Avatar uploaded successfully"}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data['image'].filename)
            return {"message": f"{extension} is not allowed"}
        except:
            traceback.print_exc()
            return {"message": "Put Avatar failed "}, 500


class Avatar(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: str):
        user_id = get_jwt_identity()
        folder = f"avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            try:
                return send_file(avatar)
            except FileNotFoundError:
                return {"message": "Avatar Not found"}, 404
        else:
            return {"message": "Avatar Not found"}, 404
