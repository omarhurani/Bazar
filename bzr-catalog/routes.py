from flask import request
from flask_app import app
from book import Book, topic_schema, item_schema, update_schema, dump_schema
from replication import replication, Replication
import cache


# Query-by-item request handler
def query_by_item(book_id):
    # Use the replication get method to make sure that the queried book is not outdated
    try:
        return replication.get(book_id)
    except Replication.CouldNotGetUpdatedError:
        return None


# Query-by-topic request handler
# The data returned by topic queries cannot be updated by end users
# so it doesn't need to be checked for different values at replicas
def query_by_topic(book_topic):
    # Use static method to get books by topic
    return Book.search(book_topic)


# Define query methods
# For each method, two fields are defined:
#   1. A query handler, which references the handler function that handles the query
#   2. A schema object, which formats the response message
queries = {
    'item': {
        'query_handler': query_by_item,
        'schema': item_schema
    },
    'topic': {
        'query_handler': query_by_topic,
        'schema': topic_schema
    }
}


# Query endpoint
@app.route('/query/<method>/<param>', methods=['GET'])
def query(method, param):
    # If the query method specified in the URI does not exist, return an error message
    if method not in queries:
        return {'message': 'Invalid query method', 'supportedQueryMethods': list(queries.keys())}, 404

    # Call the query handler and pass it the parameter from the URI
    result = queries[method]['query_handler'](param)

    # If the result is None, the query was not successful, return an error message
    if result is None:
        return {'message': 'Not found'}, 404

    # Otherwise, return the query result, formatted using the schema object
    return queries[method]['schema'].jsonify(result)


# Update endpoint
@app.route('/update/<book_id>', methods=['PUT'])
def update(book_id):
    # Extract the JSON data from the request
    book_data = request.json

    # If no data was passed (or the request was not JSON formatted), treat it like an empty JSON object
    if book_data is None:
        book_data = {}

    # This will make sure that the book to be updated is the up-to-date book consistent with other servers
    book = query_by_item(book_id)

    # If the book is None, that means that it doesn't exist in the database, so return an error message
    if book is None:
        return {'message': 'Not found'}, 404

    # Also, the order server will have the most up-to-date version of the book before modifying it
    # So the quantity updates should stay consistent across all servers

    # Use the replication method to update the book and make sure all other replicas get the updated book
    book = replication.update(book_id, book_data)

    # Invalidate cache
    cache.invalidate_item(book_id)
    cache.invalidate_topic(book.topic)

    # book = Book.update(book_id,
    #                    # title=book_data.get('title'),
    #                    quantity=book_data.get('quantity'),
    #                    # topic=book_data.get('topic'),
    #                    price=book_data.get('price'))

    # Otherwise, return the updated information of the book formatted with the schema object
    return update_schema.jsonify(book)
