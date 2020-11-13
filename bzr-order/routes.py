from flask_app import app, CATALOG_ADDRESS
import requests


# Buy endpoint
@app.route('/buy/<book_id>', methods=['PUT'])
def buy(book_id):
    # If the ID is not a number, reject the purchase
    if not book_id.isnumeric():
        return {'message': 'Book ID must be a number'}, 422

    # Query the book from the catalog server
    book_response = requests.get(f'{CATALOG_ADDRESS}/query/item/{book_id}')

    # If the response status is 404 not found, override the error message
    if book_response.status_code == 404:
        return {'message': 'Book with the specified ID does not exist'}, 404

    # If any other non-OK response is received, return it as-is
    elif book_response.status_code != 200:
        return book_response.content, book_response.status_code, book_response.headers.items()

    # Extract the book information from the response
    book = book_response.json()

    # If the quantity is 0, return that the book is out of stock
    if book['quantity'] <= 0:
        return {'success': False, 'message': 'Book with the specified ID is out of stock'}

    # Otherwise, update the book quantity on the catalog server using the update message
    buy_response = requests.put(f'{CATALOG_ADDRESS}/update/{book_id}', json={'quantity': book['quantity']-1})

    # If any error occurs while updating, return the error as-is
    if buy_response.status_code != 200:
        return buy_response.text, buy_response.status_code, buy_response.headers.items()

    # Otherwise, return a successful purchase message
    return {'success': True, 'message': 'Book with the specified ID purchased'}

