from database import db, marshmallow, database_init
from sqlalchemy import func


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False,)
    topic = db.Column(db.String(200), nullable=False,)
    quantity = db.Column(db.Integer, nullable=False, default=0,)
    cost = db.Column(db.Float, nullable=False)

    def __init__(self, title, topic, quantity, cost):
        self.title = title
        self.quantity = quantity
        self.topic = topic
        self.cost = cost

    @classmethod
    def search(cls, topic):
        return Book.query.filter(func.lower(Book.topic) == func.lower(topic))


database_init += [
    Book('How to get a good grade in DOS in 20 minutes a day', 'Distributed Systems', 10, 25.00),
    Book('RPCs for Dummies', 'Distributed Systems', 5, 50.00),
    Book('Xen and the Art of Surviving Graduate School', 'Graduate School', 10, 15.00),
    Book('Cooking for the Impatient Graduate Student', 'Graduate School', 25, 10.00)
]


class BookSearchSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title')


class BookLookupSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title', 'topic', 'quantity', 'cost')


book_lookup_schema = BookLookupSchema()
books_search_schema = BookSearchSchema(many=True)


