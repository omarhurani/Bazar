from flask_app import FRONT_END_ADDRESS
import requests


# Send a request to the front end server to invalidate a book
def invalidate_item(book_id):
    requests.put(f'{FRONT_END_ADDRESS}/invalidate/item/{book_id}')


# Send a request to the front end server to invalidate a topic
# The topic data does not change, so this is not of any use right now
def invalidate_topic(book_topic):
    requests.put(f'{FRONT_END_ADDRESS}/invalidate/topic/{book_topic}')
