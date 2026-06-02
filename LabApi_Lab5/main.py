import os
from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from models.database import db
from api.resources import BookListResource, BookResource


def create_app(config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:WeRtY54321@localhost:54321/library_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
    }
    swagger_template = {
        "info": {
            "title": "Library API",
            "description": "REST API для бібліотеки книг",
            "version": "1.0.0",
        },
        "definitions": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "description": {"type": "string"},
                    "year": {"type": "integer"},
                },
            },
            "BookInput": {
                "type": "object",
                "required": ["title", "author", "year"],
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "description": {"type": "string"},
                    "year": {"type": "integer"},
                },
            },
        },
    }

    db.init_app(app)
    Swagger(app, config=swagger_config, template=swagger_template)

    api = Api(app)
    api.add_resource(BookListResource, "/books/")
    api.add_resource(BookResource, "/books/<int:book_id>")

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)