from flask import request
from flask_restful import Resource
from flasgger import swag_from
from marshmallow import ValidationError

from repository.book_repo import BookRepository
from schemas.book import book_schema, books_page_schema

repo = BookRepository()


class BookListResource(Resource):

    def get(self):
        """
        Отримати список книг з пагінацією
        ---
        tags:
          - books
        parameters:
          - name: limit
            in: query
            type: integer
            default: 10
            minimum: 1
            maximum: 100
          - name: offset
            in: query
            type: integer
            default: 0
            minimum: 0
        responses:
          200:
            description: Список книг
            schema:
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/definitions/Book'
                total:
                  type: integer
                limit:
                  type: integer
                offset:
                  type: integer
        """
        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
            if limit < 1 or limit > 100 or offset < 0:
                return {"error": "Invalid pagination params"}, 400
        except ValueError:
            return {"error": "limit and offset must be integers"}, 400

        books, total = repo.get_all(limit=limit, offset=offset)
        return books_page_schema.dump({
            "items": [b.to_dict() for b in books],
            "total": total,
            "limit": limit,
            "offset": offset,
        }), 200

    def post(self):
        """
        Створити нову книгу
        ---
        tags:
          - books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/BookInput'
        responses:
          201:
            description: Книга створена
            schema:
              $ref: '#/definitions/Book'
          400:
            description: Помилка валідації
        """
        try:
            data = book_schema.load(request.get_json())
        except ValidationError as e:
            return {"error": e.messages}, 400

        book = repo.create(data)
        return book_schema.dump(book.to_dict()), 201


class BookResource(Resource):

    def get(self, book_id):
        """
        Отримати книгу за ID
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Книга
            schema:
              $ref: '#/definitions/Book'
          404:
            description: Книгу не знайдено
        """
        book = repo.get_by_id(book_id)
        if not book:
            return {"error": "Book not found"}, 404
        return book_schema.dump(book.to_dict()), 200

    def put(self, book_id):
        """
        Оновити книгу
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/BookInput'
        responses:
          200:
            description: Книга оновлена
            schema:
              $ref: '#/definitions/Book'
          404:
            description: Книгу не знайдено
        """
        book = repo.get_by_id(book_id)
        if not book:
            return {"error": "Book not found"}, 404

        try:
            data = book_schema.load(request.get_json())
        except ValidationError as e:
            return {"error": e.messages}, 400

        updated = repo.update(book, data)
        return book_schema.dump(updated.to_dict()), 200

    def delete(self, book_id):
        """
        Видалити книгу
        ---
        tags:
          - books
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          204:
            description: Книга видалена
          404:
            description: Книгу не знайдено
        """
        book = repo.get_by_id(book_id)
        if not book:
            return {"error": "Book not found"}, 404

        repo.delete(book)
        return "", 204