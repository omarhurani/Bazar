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

    # Clear all entries from cache
    def clear(self):
        self.cache.clear()
        self.lru_queue.clear()

    # Get all keys of cached items
    def ids(self):
        return list(self.lru_queue)

    # Check if id exists in cache
    def __contains__(self, id):
        return id in self.cache


# Define class for search entry
class SearchEntry:
    def __init__(self, search_result):
        # Set of topics stored in this entry
        # This is needed to invalidate the topic when necessary
        self.topics = set([book['topic'] for book in search_result])

        # The entry itself
        self.search_result = search_result

    def __contains__(self, item):
        return item in self.topics


lookup_cache = Cache()
search_cache = Cache(max_size=10)


# Route used by catalog servers to invalidate book entries
@app.route('/invalidate/item/<book_id>', methods=['DELETE'])
def invalidate_item(book_id):
    # If book is cached, remove it
    if book_id in lookup_cache:
        lookup_cache.remove(int(book_id))

    return '', 204


# Route used by catalog servers to invalidate all cached book topics
# This is used when a new book is added, since it might appear in search caches

# There could be a better algorithm to find out if the book can exist in the search
# results, but this is a simpler approach
@app.route('/invalidate/topic/', methods=['DELETE'])
def invalidate_all_topics():
    # Remove any entry containing this topic
    search_cache.clear()
    return '', 204


# Route used by catalog servers to invalidate book topics
@app.route('/invalidate/topic/<book_topic>', methods=['DELETE'])
def invalidate_topic(book_topic):

    containing_entries = [key for key, value in search_cache.cache.items()
                          if book_topic in value.topics]

    # Remove any entry containing this topic
    for entry in containing_entries:
        search_cache.remove(entry)

    return '', 204


# Test endpoint that dumps all the cache contents
@app.route('/dump/', methods=['GET'])
def dump():
    response = {
        'lookup': [{'id': id, **lookup_cache.cache[id]} for id in lookup_cache.lru_queue],
        'search': [{'id': id,
                    'topics': list(search_cache.cache[id].topics),
                    'search_result': search_cache.cache[id].search_result}
                   for id in search_cache.lru_queue]
    }
    print(response)
    return response
