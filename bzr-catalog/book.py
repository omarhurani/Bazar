from database import db, marshmallow, database_init


# Define the Book class that overrides SQLAlchemy's Model class
class Book(db.Model):
    # Define the Book fields which will be mapped to database columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False,)
    topic = db.Column(db.String(200), nullable=False,)
    quantity = db.Column(db.Integer, nullable=False, default=0,)
    price = db.Column(db.Float, nullable=False)

    # Replication field for consistency
    sequence_number = db.Column(db.Integer, nullable=False, default=0,)

    # Constructor
    def __init__(self, title, topic, quantity, price):
        self.title = title
        self.quantity = quantity
        self.topic = topic
        self.price = price
        self.sequence_number = 0

    # Static method to search for books based on the topic
    @classmethod
    def search(cls, topic):
        # Returns books that contain the query string, ignoring case
        return Book.query.filter(Book.topic.ilike(f'%{topic}%'))

    # Static method to get a book using its ID
    @classmethod
    def get(cls, id):
        return Book.query.get(id)

    # Static method to update the fields of a book given its ID
    # If the field is not passed (or passed as None), it will not be affected
    @classmethod
    def update(cls, id, title=None, quantity=None, topic=None, price=None, sequence_number=None):
        book = Book.query.get(id)
        if book is None:
            return None
        book.title = title if title is not None else book.title
        book.quantity = quantity if quantity is not None and quantity >= 0 else book.quantity
        book.topic = topic if topic is not None else book.topic
        book.price = price if price is not None and price >= 0.0 else book.price

        # Update sequence number of book
        if sequence_number is None:
            if title is not None or quantity is not None or topic is not None or price is not None:
                book.sequence_number = book.sequence_number + 1
        else:
            book.sequence_number = sequence_number

        db.session.commit()
        return book


# Add the 7 books as an initial entry to the database
database_init += [
    Book('How to get a good grade in DOS in 20 minutes a day', 'Distributed Systems', 10, 25.00),
    Book('RPCs for Dummies', 'Distributed Systems', 5, 50.00),
    Book('Xen and the Art of Surviving Graduate School', 'Graduate School', 10, 15.00),
    Book('Cooking for the Impatient Graduate Student', 'Graduate School', 25, 10.00),
    Book('How to finish Project 3 on time', 'University Problems', 25, 10.00),
    Book('Why theory classes are so hard', 'University Problems', 25, 10.00),
    Book('Spring in the Pioneer Valley', 'Developer Life', 25, 10.00),
]


# Define Marshmallow Formatter Schema class for query-by-topic response fields
class TopicSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title', 'topic')


# Define Marshmallow Formatter Schema class for query-by-item response fields
class ItemSchema(marshmallow.Schema):
    class Meta:
        fields = ('title', 'quantity', 'price')


# Define Marshmallow Formatter Schema class for update response fields
class UpdateSchema(marshmallow.Schema):
    class Meta:
        fields = ('title', 'quantity', 'topic', 'price')


# Define Marshmallow Formatter Schema class for replication consistency:
class ReplicationSchema(marshmallow.Schema):
    class Meta:
        fields = ('sequence_number', 'title', 'quantity', 'topic', 'price')


# Instantiate an object from each schema class
item_schema = ItemSchema()
topic_schema = TopicSchema(many=True)
update_schema = UpdateSchema()
replication_schema = ReplicationSchema()


