from flask import jsonify
from flask_app import app
from book import Book, books_search_schema, book_lookup_schema


# Search endpoint
@app.route('/search/<book_topic>', methods=['GET'])
def search(book_topic):
    books = Book.search(book_topic)
    return jsonify(books_search_schema.dump(books))


# Lookup endpoint
@app.route('/lookup/<book_id>', methods=['GET'])
def lookup(book_id):
    book = Book.get(book_id)
    if book is None:
        return {'message': 'Book with the specified ID was not found'}, 404
    return book_lookup_schema.jsonify(book)


# Buy endpoint
@app.route('/buy/<book_id>', methods=['POST', 'PUT'])
def buy(book_id):
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422
    try:
        book = Book.buy(book_id)
        if book is None:
            return {'message': 'Book with the specified ID was not found'}, 404
        return {
            'status': 'Success',
            'message': 'Book purchased successfully'
        }
    except Book.OutOfStockError:
        return {
            'status': 'Failure',
            'message': 'Book is out of stock'
        }


