from flask import Blueprint

posts = Blueprint("post", __name__, url_prefix="/api/v1/posts")


@posts.get("/")
def get_all():
    return {"posts": []}
