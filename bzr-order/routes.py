from flask import make_response
from flask_app import app, CATALOG_ADDRESS
import requests


@app.route('/buy/<book_id>', methods=['PUT'])
def buy(book_id):
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422
    book_response = requests.get(f'{CATALOG_ADDRESS}/query/item/{book_id}')
    if book_response.status_code == 404:
        return {'message': 'Book with the specified ID does not exist'}, 404
    elif book_response.status_code != 200:
        return book_response.content, book_response.status_code, book_response.headers.items()
    book = book_response.json()
    if book['quantity'] <= 0:
        return {'success': False, 'message': 'Book with the specified ID is out of stock'}
    buy_response = requests.put(f'{CATALOG_ADDRESS}/update/{book_id}', json={'quantity': book['quantity']-1})
    if buy_response.status_code != 200:
        return buy_response.text, buy_response.status_code, buy_response.headers.items()
    return {'success': True, 'message': 'Book with the specified ID purchased'}

