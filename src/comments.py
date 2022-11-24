from flask import Blueprint

comments = Blueprint("comment", __name__, url_prefix="/api/v1/comments")


@comments.get("/")
def get_all():
    return {"comments": []}
