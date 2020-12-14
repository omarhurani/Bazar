from flask_app import app


# Defines the cache
class Cache:
    def __init__(self, max_size: int = 3):
        self.cache = {}
        self.lru_queue = []
        self.max_size = max_size

    # Insert item into cache
    def insert(self, id, data):
        # If item already exists in cache, remove it (to reinsert later)
        if id in self:
            self.cache.pop(id)
            self.lru_queue.remove(id)

        # If cache doesn't fit more items, pop the least recently used
        if len(self.cache) >= self.max_size:
            remove_book_id = self.lru_queue.pop(0)
            self.cache.pop(remove_book_id)

        # Add the item to the cache and the front of the LRU queue
        self.cache[id] = data
        self.lru_queue.append(id)

    # Get item from cache
    def get(self, id):
        # If item is not in cache return None
        if id not in self.cache:
            return None

        # Bring item to the front of the LRU queue
        self.lru_queue.remove(id)
        self.lru_queue.append(id)

        # Return item from cache
        return self.cache[id]

    # Remove item from cache
    def remove(self, id):
        if id in self.cache:
            self.cache.pop(id)
            self.lru_queue.remove(id)

    # Get all keys of cached items
    def ids(self):
        return list(self.lru_queue)

    # Check if id exists in cache
    def __contains__(self, id):
        return id in self.cache


lookup_cache = Cache()
search_cache = Cache(max_size=10)


# Route used by catalog servers to invalidate book entries
@app.route('/invalidate/item/<book_id>', methods=['PUT'])
def invalidate_item(book_id):
    # If book is cached, remove it
    lookup_cache.remove(int(book_id))

    return {}


# Route used by catalog servers to invalidate book topics
@app.route('/invalidate/topic/<book_topic>', methods=['PUT'])
def invalidate_topic(book_topic):
    # If topic is cached, remove it
    search_cache.remove(book_topic.lower())

    return {}


# Test endpoint that dumps all the cache contents
@app.route('/dump/', methods=['GET'])
def dump():
    response = {
        'lookup': [{'id': id, **lookup_cache.cache[id]} for id in lookup_cache.lru_queue],
        'search': [{'id': id, 'books': search_cache.cache[id]} for id in search_cache.lru_queue]
    }
    print(response)
    return response