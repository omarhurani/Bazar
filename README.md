# Bazar
 **Bazar** is a multi-tier online book store created for the fulfillment of the **Distrubed Operating Systems (DOS)** course.


In **Bazar**, you can search for books based on topics and look up book details and make orders.


## Architecture
**Bazar** consists of 3 microservices:
1. **Catalog Service:** This service communicates directy with the database and exposes resources to query and update book entries.
2. **Order Service:** This service handles any orders made by the user. It makes sure that the requested book exists in the catalog and has enough stock.
3. **Front-end Service:** This service is the service which the user communicates with to use **Bazar**. It exposes search and look-up resources that communicate directly with the catalog service, and a buy resource which communicates with the order service.

## Implementation
### Frameworks and Libraries
**Bazar** was implemented using [Flask](https://flask.palletsprojects.com/en/1.1.x/), a [Python](https://www.python.org/) framework for micro web services.

For the order and front-end services, the only other Python library needed is [requests](https://requests.readthedocs.io/en/master/) for them to communicate with other services. 


For the catalog server, a database management library is needed. [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) is a **Flask** extension that adds support for the [SQLAlchemy](https://www.sqlalchemy.org/) library, which is an **Object Relational Mapper** that allows for interaction with SQL databases through model objects, without the need of using any SQL statements. [Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/) was also used, which is adds support for the [Marshmallow](https://marshmallow.readthedocs.io/en/stable/) object serialization/ deserialization library, which helps in object representation. For **SQLAlchemy** and **Marshmallow** to work together, the [Marshmallow-SQLAlchemy](https://marshmallow-sqlalchemy.readthedocs.io/en/latest/) was used, allowing integration between the two. An [SQLite](https://www.sqlite.org/index.html) database was used, since it is lightweight and can be stored in one file.

### How it works
#### Catalog Service
This service exposes two end-points for the other services to use, `query` and `update`.


The `query` end-point can receive two types of `GET` requests, `query/item` and `query/topic`.`query/topic` receives a search text in the URI, and looks it up in the database using an `ilike` filter. It responds with a list of the books found with that topic. If no books were found, it responds with an empty list. `query/item` receives the ID of the book to look up in the URI, and responds with the book if it was found, or with an `404 NOT FOUND` status code if it doesn't exist in the database. 


The `update` end-point receives `PUT` requests to modify book entries. Any of the fields, excluding the ID, can be modified through it by passing them in a JSON object. Any fields that are not passed do not get modified. The book ID is received in the URI. The endpoint responds with the new book fields in a JSON object if that book exists, or with an `404 NOT FOUND` status code if it doesn't.


#### Order Service
This service exposes just one endpoint, `buy`. It receives a `PUT` request with the book ID in the URI. It checks whether the ID is numeric with not, and declines the request if it isn't. Then, it queries the catalog service by item to get the book entry associated with that ID. If it was found, it checks its quantity. If the quantity is sufficent, it requests an update of the quantity of the item, decreasing it by one. If not, it replies with a messaging that the book is out of stock.


#### Front-End Service
This services exposes the endpoints used by the end-user, `search`, `lookup` and `buy`. The `search` endpoint receives the search topic in the URI as a `GET` request and forwards the request as a `query/topic` request to the catalog service. The `lookup` endpoint receives the book ID in the URI as a `GET` request, checks if it is numeric and forwards it to the catalog server as a `query/item` request. The `buy` endpoint is the same as the `lookup` endpoint, but requests have to use the `PUT` method, and they're forwarded to the `buy` endpoint on the order service.


### Limitations
In the current design of the microservices, all the services are completely exposed for any party to use. This means that if someone where to dig out the `update` endpoint on the catalog server, they can modify any field of any book. This can be solved by multiple ways. Some authentication between the services could be used in order for them to identify whether they're communicating with each other or with a third party. Another way is to host the catalog service only locally, and not expose its endpoints outside its local network. This however will force other services to be in the same local network, either physically, or through a **Virtual Private Network (VPN)**.

## Usage
### Installation and running
First, make sure that you have **Python** installed on your device(s). **Python 3.7** or higher is recommended. You can download and install **Python** from [here](https://www.python.org/downloads/).


Next, install **pip** if you don't have it on your device from [here](https://pip.pypa.io/en/stable/installing/). Note that for **Python 3**, **pip3** is needed.


Each microservice is in its own folder. It is recommended to create a virtual environment for each service if you want to run them all on the same device, but it is optional. You can learn about Python virtual environments [here](https://docs.python.org/3/tutorial/venv.html).


For each service, install the required Python packages using pip:
#### Python 2
```
pip install -r /path/to/microservice/folder/requirements.txt
```
#### Python 3
```
pip3 install -r /path/to/microservice/folder/requirements.txt
```


The microservices also use some environment variables in order to configure the service. Make sure to set up **all** these environment variables on your device(s) or virtual environment of each services before running the services (even if they might not seem required).

Environment Variable | Description | Example
-------------------- | ----------- | -------
`CATALOG_ADDRESS` | The address of the catalog service. Used in the order and front-end services. | `http://192.168.1.100:5000`
`ORDER_ADDRESS` | The address of the order service. Used in the front-end and catalog services. | `http://192.168.1.101:5000`
`FRONT_END_ADDRESS` | The address of the front-end service. Used in the catalog and order services. | `http://192.168.1.102:5000`
`FLASK_ENV` | Define the enviroment of the Flask application. Can be `development` or `production`. `development` enables the use of debug mode. | `development`
`FLASK_DEBUG` | Enable debug mode or not. In debug mode, modifications to the Flask application files automatically refreshes the service. Requires `FLASK_ENV` to be set to `development`. Can be `True` or `False`. | `True`
`FLASK_PORT` | Define the port number used by the microservice. | `5000`


To run each microservice:
#### Python 2
```
python /path/to/microservice/folder/app.py
```

#### Python 3
```
python3 /path/to/microservice/folder/app.py
```

### API Usage

All services primarily use JSON to format the data. Make sure to include `Content-Type: application/json` in their request header.

#### Catalog
URI | Methods | Description
--- | ------- | -----------
`/query/item/<id>` | `GET` | Query a book using its `id`. Returns a single JSON object containing book information if successful.
`/query/topic/<topic>` | `GET` | Query books using their topic. Returns a list of JSON objects containing book IDs, names and topics.
`/update/<id>` | `PUT` | Update book using its `id` based on fields sent in the request body. Returns the updated book fields if successful.


#### Order
URI | Methods | Description
--- | ------- | -----------
`/buy/<id>` | `PUT` | Request to purchase a book using its `id`. Returns a JSON object with a `success` field determining whether the operation was succesful or not and a `message` field to describe what happened. `id` must be a number.


#### Front-end
URI | Methods | Description
--- | ------- | -----------
`/lookup/<id>` | `GET` | Look up a book using its ID. Returns a single JSON object containing book information if successful. `id` must be a number.
`/search/<topic>` | `GET` | Search for books using their `topic`. Returns a list of JSON objects containing book IDs, names and topics.
`/update/<id>` | `PUT` | Request to purchase a book using its `id`. Returns a JSON object with a `success` field determining whether the operation was succesful or not and a `message` field to describe what happened. `id` must be a number.

## Example
In this example, the sequence of actions is as follows:
1. Search for books with search query `t`.
2. Further specify the search by searching for books with search query `distributed`, and choose the second book from the list to use in the next steps.
3. Look up the details of the selected book.
4. Order the selected book.
5. Look up the details of the selected book again to make sure its stock got reduced.
6. Keep ordering the book until it runs out of stock.
7. Attempt to look up (or buy) a non-numeric book ID.
8. Attempt to look up (or buy) a non-existent book ID.


The address of the front-end service is `http://192.168.1.102:5000`.


---

### 1. Search for books with search query `t`

#### cURL Request

```
curl -H "Content-Type: application/json" --request GET http://192.168.1.102:5000/search/t
```

#### Response

`200`
```json
[
  {
    "id": 1,
    "title": "How to get a good grade in DOS in 20 minutes a day",
    "topic": "Distributed Systems"
  },
  {
    "id": 2,
    "title": "RPCs for Dummies",
    "topic": "Distributed Systems"
  },
  {
    "id": 3,
    "title": "Xen and the Art of Surviving Graduate School",
    "topic": "Graduate School"
  },
  {
    "id": 4,
    "title": "Cooking for the Impatient Graduate Student",
    "topic": "Graduate School"
  }
]
```

---

### 2. Further specify the search by searching for books with search query `distributed`, and choose the second book from the list to use in the next steps

#### cURL Request

```
curl -H "Content-Type: application/json" --request GET http://192.168.1.102:5000/search/distributed
```

#### Response

`200`
```json
[
  {
    "id": 1,
    "title": "How to get a good grade in DOS in 20 minutes a day",
    "topic": "Distributed Systems"
  },
  {
    "id": 2,
    "title": "RPCs for Dummies",
    "topic": "Distributed Systems"
  }
]
```

So we're going to use book `2` for the following steps.

---

### 3. Look up the details of the selected book

#### cURL Request

```
curl -H "Content-Type: application/json" --request GET http://192.168.1.102:5000/lookup/2
```

#### Response

`200`
```json
{
  "price": 50.0,
  "quantity": 2,
  "title": "RPCs for Dummies"
}
```

There are 2 of this book in stock.

---

### 4. Order the selected book

#### cURL Request
```
curl -H "Content-Type: application/json" --request PUT http://192.168.1.102:5000/buy/2
```

#### Response

`200`
```json
{
  "message": "Book with the specified ID purchased",
  "success": true
}
```

---

### 5. Look up the details of the selected book again to make sure its stock got reduced.

#### cURL Request
```
curl -H "Content-Type: application/json" --request GET http://192.168.1.102:5000/lookup/2
```

#### Response
`200`
```json
{
  "price": 50.0,
  "quantity": 1,
  "title": "RPCs for Dummies"
}
```

We can notice that the stock went down to 1.

---

### 6. Keep ordering the book until it runs out of stock.

#### First cURL Request
```
curl -H "Content-Type: application/json" --request PUT http://192.168.1.102:5000/buy/2
```

#### First Response
`200`
```json
{
  "message": "Book with the specified ID purchased",
  "success": true
}
```


#### Second cURL Request
```
curl -H "Content-Type: application/json" --request PUT http://192.168.1.102:5000/buy/2
```

#### Second Response
`200`
```json
{
  "message": "Book with the specified ID is out of stock",
  "success": false
}
```

---

### 7. Attempt to look up (or buy) a non-numeric book ID.

#### cURL Request
```
curl -H "Content-Type: application/json" --request GET http://192.168.1.102:5000/lookup/test
```

#### Response
```422```
```json
{
  "message": "Book ID must be a number"
}
```

The response is the same for the `buy` endpoint.

---

### 8. Attempt to look up (or buy) a non-existent book ID.

#### cURL Request
```
curl -H "Content-Type: application/json" --request PUT http://192.168.1.102:5000/buy/80
```

#### Response
`404`
```json
{
  "message": "Book with the specified ID does not exist"
}
```

