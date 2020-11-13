from flask import request
from flask_app import app
from book import Book, topic_schema, item_schema, update_schema


def query_by_item(book_id):
    return Book.get(book_id)


def query_by_topic(book_topic):
    return Book.search(book_topic)


queries = {
    'item': {
        'query_method': query_by_item,
        'schema': item_schema
    },
    'topic': {
        'query_method': query_by_topic,
        'schema': topic_schema
    }
}


@app.route('/query/<method>/<param>', methods=['GET'])
def query(method, param):
    if method not in queries:
        return {'message': 'Invalid query method', 'supportedQueryMethods': list(queries.keys())}, 404
    result = queries[method]['query_method'](param)
    if result is None:
        return {'message': 'Not found'}, 404
    return queries[method]['schema'].jsonify(result)


@app.route('/update/<book_id>', methods=['PUT'])
def update(book_id):
    book_data = request.json
    if book_data is None:
        book_data = {}
    book = Book.update(book_id,
                       title=book_data.get('title'),
                       quantity=book_data.get('quantity'),
                       topic=book_data.get('topic'),
                       price=book_data.get('price'))
    if book is None:
        return {'message': 'Not found'}, 404
    return update_schema.jsonify(book)
