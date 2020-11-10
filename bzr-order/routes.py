from flask import make_response
from flask_app import app, CATALOG_ADDRESS
import requests


@app.route('/buy/<book_id>', methods=['PUT'])
def buy(book_id):
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422
    book_request = requests.get(f'{CATALOG_ADDRESS}/lookup/{book_id}')
    if book_request.status_code != 200:
        return book_request.content, book_request.status_code, book_request.headers.items()
    buy_request = requests.put(f'{CATALOG_ADDRESS}/buy/{book_id}')
    return buy_request.text, buy_request.status_code, buy_request.headers.items()
