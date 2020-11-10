from flask_app import app, CATALOG_ADDRESS, ORDER_ADDRESS
import requests


@app.route('/search/<book_topic>', methods=['GET'])
def search(book_topic):
    response = requests.get(f'{CATALOG_ADDRESS}/search/{book_topic}')
    return response.text, response.status_code, response.headers.items()


@app.route('/lookup/<book_id>', methods=['GET'])
def lookup(book_id):
    response = requests.get(f'{CATALOG_ADDRESS}/lookup/{book_id}')
    return response.text, response.status_code, response.headers.items()


@app.route('/buy/<book_id>', methods=['PUT', 'POST'])
def buy(book_id):
    response = requests.put(f'{ORDER_ADDRESS}/buy/{book_id}')
    return response.text, response.status_code, response.headers.items()
