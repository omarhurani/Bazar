from flask_app import app, CATALOG_ADDRESS, ORDER_ADDRESS
import requests


@app.route('/search/<book_topic>', methods=['GET'])
def search(book_topic):
    response = requests.get(f'{CATALOG_ADDRESS}/query/topic/{book_topic}')
    return response.text, response.status_code, response.headers.items()


@app.route('/lookup/<book_id>', methods=['GET'])
def lookup(book_id):
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422
    response = requests.get(f'{CATALOG_ADDRESS}/query/item/{book_id}')
    if response.status_code == 404:
        return {'message': 'Book with the specified ID does not exist'}, 404
    return response.text, response.status_code, response.headers.items()


@app.route('/buy/<book_id>', methods=['PUT'])
def buy(book_id):
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422
    response = requests.put(f'{ORDER_ADDRESS}/buy/{book_id}')
    return response.text, response.status_code, response.headers.items()
