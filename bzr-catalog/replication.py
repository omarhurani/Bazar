import random

from flask_app import CATALOG_ADDRESSES, app
from requests import RequestException
from book import Book, replication_schema
from flask import request

import requests


timeout = 0.2


class Replication:

    class CouldNotGetUpdatedError(RuntimeError):
        pass

    class OutdatedUpdateError(RuntimeError):
        pass

    def __init__(self, catalog_addresses):
        self.catalog_addresses = catalog_addresses
        if type(self.catalog_addresses) is not list:
            self.catalog_addresses = []
        self.updated_ids = set([])

    def update(self, id, book_info) -> Book:
        # If no other catalog servers are registered, no need for replication measures
        if len(self.catalog_addresses) == 0:
            return Book.update(id,
                               # title=book_data.get('title'),
                               quantity=book_info.get('quantity'),
                               # topic=book_data.get('topic'),
                               price=book_info.get('price'))

        sequence_number = Book.get(id).sequence_number

        # If book is not recorded as up-to-date
        if id not in self.updated_ids:
            # Check servers for latest version of book
            max_sequence_number = sequence_number
            max_item = None

            for server in self.catalog_addresses:
                # Should spawn threads to handle multiple concurrent requests
                try:
                    # Request other servers to check the book sequence_number
                    data = {'sequence_number': sequence_number}
                    response = requests.get(f'{server}/rep/check/{id}',
                                            json=data, timeout=timeout)

                    # If object is out of date, update the object of maximum sequence number
                    if response.status_code == 409:
                        if max_sequence_number < response.json()['sequence_number']:
                            max_sequence_number = response.json()['sequence_number']
                            max_item = response.json()

                # Ignore non-alive servers
                except RequestException:
                    pass

            # After checking with servers, book might be in 2 states:

            # 1. Up-to-date: Just mark it as up-to-date

            # 2. Out-of-date: Server responds with the up-to-date book
            # so local book is updated to the most up-to-date version

            # In both states, book should be marked as up-to-date
            self.updated_ids.add(id)

            # If one of the checks fails
            if max_item is not None:
                # Update local book with the failed book
                Book.update(id, **max_item)

                # Raise an error that the update request wasn't valid
                raise self.OutdatedUpdateError()

        # If none of the checks fail, send an update request to all servers
        for server in self.catalog_addresses:
            # Should spawn threads to handle multiple concurrent requests
            try:
                # Request other servers to update the book
                data = {'sequence_number': sequence_number, **book_info}
                response = requests.put(f'{server}/rep/update/{id}',
                                        json=data, timeout=timeout)

                # If object is out of date, raise an error that the update wasn't valid
                if response.status_code == 409:
                    raise self.OutdatedUpdateError()

            # Ignore non-alive servers
            except RequestException:
                pass

        # Update the local book with the information
        book = Book.update(id, **book_info)

        # Mark book as updated
        self.updated_ids.add(id)

        return book

    def get(self, id, requesters: list = None) -> Book:
        # If item is tracked as up-to-date, return
        if id in self.updated_ids:
            return Book.get(id)

        if requesters is None:
            requesters = []

        # Filter out all servers which were requested before for this item
        available_servers = self.catalog_addresses if requesters is None else \
            [server for server in self.catalog_addresses if server not in requesters]
             # if len([requester for requester in requesters if IPNetwork(server) == IPNetwork(requester)]) == 0]

        # If no server was left, assume copy of this server is the correct copy
        if len(available_servers) == 0:
            return Book.get(id)

        # Send a read request of the most up-to-date book to a random catalog server
        server = None
        while len(available_servers) > 0:
            try:
                server = random.choice(available_servers)
                response = requests.get(f'{server}/rep/get/{id}',
                                        json={'requesters': requesters if requesters is not None else []},
                                        timeout=timeout)
                break
            except RequestException:
                if server is not None:
                    available_servers.remove(server)

        # If no server was left, assume copy of this server is the correct copy
        else:
            return Book.get(id)

        # If the item could not be retrieved raise an error
        if response.status_code != 200:
            raise self.CouldNotGetUpdatedError()

        # Update the book with the retrieved book
        Book.update(id, **response.json())

        # Mark this item as updated
        self.updated_ids.add(id)

        return Book.get(id)

    def get_catalog_addresses_pure(self):
        return [address.replace('http://', "").replace('https://', "") for address in self.catalog_addresses]


replication = Replication(CATALOG_ADDRESSES)


@app.route('/rep/update/<book_id>', methods=['PUT'])
def replication_update(book_id):
    book_info = request.json

    book_id = int(book_id)

    book = Book.get(book_id)

    # If local book is newer than the edit request, reject update
    if book.sequence_number > book_info['sequence_number']:
        return replication_schema.jsonify(book), 409  # 409 Conflict

    # Update the book with the retrieved book
    Book.update(book_id, **book_info)

    # Server responds with the old sequence number, so format response before updating
    response = replication_schema.jsonify(Book.get(book_id))

    # Update sequence number manually
    Book.update(book_id, sequence_number=book_info['sequence_number']+1)

    return response


@app.route('/rep/get/<book_id>', methods=['GET'])
def replication_get(book_id):

    # Get list of servers that are requesting this item
    requesters = []
    if request.json is dict and 'requesters' in request.json:
        requesters = list(request.json['requesters'])

    # Add the remote address (the server who sent this request) to the list
    requesters.extend([address for address in replication.catalog_addresses if request.remote_addr in address])

    try:
        # Get the book from replication
        book = replication.get(int(book_id), requesters=requesters)

    # If book could not be retrieved (nobody has it)
    except Replication.CouldNotGetUpdatedError:
        return {'message': 'Not found'}, 404

    if book is None:
        return {'message': 'Not found'}, 404

    return replication_schema.jsonify(book)


@app.route('/rep/check/<book_id>', methods=['GET'])
def replication_check(book_id):
    book_info = request.json

    book_id = int(book_id)

    book = Book.get(book_id)

    # If local book is newer than the check request, respond that its not valid
    if book.sequence_number > book_info['sequence_number']:
        return replication_schema.jsonify(book), 409  # 409 Conflict

    return {}
