# Bazar V2

Make sure to have read [Bazar V1 documentation](https://github.com/omarhurani/Bazar/blob/V1/README.md) prior to reading this.

---

## Caching

Caching was implemented in the front-end server using a Python dictionary (`dict`) and list (`list`). The dictionary is to store key-value pairs of the cache, and the list to act as a **Least Recently Used (LRU)** queue for the cache replace policy.

### Lookup Caching

Caching book lookups was simple. The key was the ID of the book and the value was the returned JSON object of that book. An end-point is introduced in order for catalog servers to invalidate the lookup cache. This end-point receives the book ID as a paramters and removes the cache entry with that ID if it exists in cache.

In the catalog server, when an update is performed on a book, it sends a request with the ID of that book to the invalidation end-point of the front-end server in order to remove it from its cache. This also implies that the catalog server needs to know the address of the front-end server, so it is added to the environment variables needed for it.

The following figures demonstrate how lookup caching operates.

### Search Caching

Caching search results is a little bit more tricky, since changes to a book could invalidate a whole topic (however, in Bazar, updates done don't modify fields that are returned in search results, so invalidating is not nessecary, but I implemented it anyways). I approached this problem by using the search string as the key, and the entry being two things, the JSON response of the search operation, and a set of all topics included in that response. When the catalog server sends an invalidate request for a topic on its end-point in the front-end server, all cached items are checked for their topic set, and any topic set that includes that topic are removed from the cache. Another end-point was added that allows catalog servers to clear the cache completely. This is useful when a new book needs to be added in the future.

The following figures demonstrate how search caching operates.

---

## Replication

### Catalog Servers

The first modification made to the catalog server was the needed environment variables, since it nows needs to know the addresses of the other catalog servers.

Environment Variable | Description | Example
-------------------- | ----------- | -------
`CATALOG_ADDRESSES` | The addresses of the other catalog servers. Addresses are seperated by a `\|` character | `http://catalog2.bazar.com\| http://catalog2.bazar.com`


Consistency issues rise in both read and write operations.

#### **Sequence Numbers**

In order for servers to keep track of the versions of the books they have, a sequence number field for each was introduced. This field is used to compare versions between servers in order to maintain consistency.

#### **Read**

If a catalog server goes down for some time and then goes back up, the data inside it might become outdated due to writes on other replicas that did not encounter outage.

In order to handle this issue, each server kept an in-memory list of all books that are validated to be consistent with other copies. This list starts out empty. Whenever a read request is received, the list is checked. If the ID of that book exists, it responds with the locally-stored book. If not, it selects a random catalog server and sends a request to it in order to retreive the up-to-date book. This request will keep hopping over between servers until either a server with the book marked as valid is found or no more servers are left.

If a server with the valid book was found, that server returns all the information about the book in the response, and its updated in all servers that requested it.

If no servers are left, the last server in the chain considers its version the correct version and returns its book in the response. This situation can only occur in 2 cases:

1. **Cold Start**: when Bazar is deployed for the first time, all catalog servers will have their valid list empty. In this case, the databases for all catalog servers are matching.

2. **Total Failure**: when all catalog servers fail at the same time and restart. Read requests will hop between catalog servers until they reach a dead-end, and end up selecting books with the highest sequence number to be used.

The following figures demonstrate how read requests flow between catalog servers.

[Figures]

#### **Write**

Catalog servers need to make sure that any write persists on all replicas to maintain consistency. They also use the same updated list to make sure that their copy is consistent.

If their copy is not up-to-date, a different approach was used than the read approach. A catalog server will send a check request to all other catalog servers to check the sequence numbers of the objects they have. The servers respond with an OK message if the sequence number they receive is larger than or equal to their current one (indicating that a write can be performed), and a Conflict response if their current sequence number is larger than the one received in the check request, alongside with the object data. The original server. If all recevied responses were OK, the server can proceed with updating the value. If not, it updates its local value with the most up-to-date object (the object with max sequence number between all Conflict responses) and returns a Conflict response, telling its requester that the write could not be performed for them to retry. This is important because the order server calculates the new stock value when an order is performed, and has to be informed that the catalog server had outdated information in order for it to re-calculate the new stock and retry the write operation.

After that, if the catalog server is still proceeding with the write operation (has object marked as up-to-date or had a writable sequence number for all ohter instances), it proceeds to send a replication update message to all other catalog servers with the new information. It ignores downed servers.

The following figures demonstrate how write requests are handled.

[Figures]

### Order Servers

Each order server communicates with one catalog server. If it can't reach it, it returns a Gateway Timeout error. It functions mostly the same as V1. The only difference is that checks if the write response error code is a Conflict error, it fetches the book again and repeats the attempt to write the book with a quantity reduced by one.

The following figures demonstrate how order requests are handled.

[Figures]

### Front-end Server

Changes to the front-end server are more than the changes to the order servers, but still not major. First, the environment variables now support multiple catalog and order servers.

Environment Variable | Description | Example
-------------------- | ----------- | -------
`CATALOG_ADDRESSES` | The addresses of the catalog servers. Addresses are seperated by a `\|` character | `http://catalog1.bazar.com\| http://catalog2.bazar.com\| http://catalog3.bazar.com`
`ORDER_ADDRESSES` | The addresses of the order servers. Addresses are seperated by a `\|` character | `http://order1.bazar.com\| http://order2.bazar.com\| http://order3.bazar.com`

After they are imported, they are used in a round-robin fassion. The front-end server attempts to connect with the server with the current turn, and proceeds normally if successful. Otherwise, it tries the other servers one by one. If none can be reached, it returns a Gateway Timeout error response.

The following figures demonstrate how replication is handled at the front-end side.

[Figures]

---

## Metrics

