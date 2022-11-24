from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_401_UNAUTHORIZED
import validators
from src.database import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
def register():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password = request.json['password']

    if not firstname or not lastname:
        return jsonify({"error": "firstname and lastname are required"}), HTTP_400_BAD_REQUEST

    if len(password) < 8:
        return jsonify({"error": "Password is to short"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = User(firstname=firstname, lastname=lastname, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully",
                    "data": {"id": user.id,
                             "email": email,
                             "firstname": firstname,
                             "lastname": lastname
                             }
                    }
                   ), HTTP_201_CREATED


@auth.post("/login")
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        return {"error": "Email is required"}, HTTP_400_BAD_REQUEST

    if not password:
        return {"error": "Password  is required"}, HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if user:
        is_password_correct = check_password_hash(user.password, password)
        if is_password_correct:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {
                       "data": {
                           "email": user.email,
                           "refresh": refresh_token,
                           "access": access_token,
                       }
                   }, HTTP_200_OK
    return jsonify({'error': "Bad credentials"}), HTTP_401_UNAUTHORIZED


@auth.get('/<int:user_id>')
@jwt_required()
def get_single_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({
            "data": {
                "user": {
                    "email": user.email,
                    "firstname": user.firstname,
                    "lastname": user.lastname
                }
            }
        }), HTTP_200_OK
    return jsonify({"error": "User not found"}), HTTP_400_BAD_REQUEST


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        "access": access
    }), HTTP_200_OK
