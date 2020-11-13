from flask_app import app, CATALOG_ADDRESS, ORDER_ADDRESS
import requests


# Search endpoint
@app.route('/search/<book_topic>', methods=['GET'])
def search(book_topic):
    # Get book from the catalog server
    response = requests.get(f'{CATALOG_ADDRESS}/query/topic/{book_topic}')

    # Return the catalog server response as-is
    return response.text, response.status_code, response.headers.items()


# Lookup endpoint
@app.route('/lookup/<book_id>', methods=['GET'])
def lookup(book_id):
    # If the ID is not a number, reject the lookup
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422

    # Get the list of books from the catalog server
    response = requests.get(f'{CATALOG_ADDRESS}/query/item/{book_id}')

    # If the response status is 404 not found, override the error message
    if response.status_code == 404:
        return {'message': 'Book with the specified ID does not exist'}, 404

    # Otherwise, return the catalog server response as-is
    return response.text, response.status_code, response.headers.items()


# Buy endpoint
@app.route('/buy/<book_id>', methods=['PUT'])
def buy(book_id):
    # If the ID is not a number, reject the purchase request
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422

    # Forward the request to the order server
    response = requests.put(f'{ORDER_ADDRESS}/buy/{book_id}')

    # Return the response from the order server as-is
    return response.text, response.status_code, response.headers.items()
