from flask import jsonify
from flask_app import app
from book import Book, books_search_schema


@app.route('/search/<topic>')
def search(topic):
    books = Book.search(topic)
    return jsonify(books_search_schema.dump(books))
