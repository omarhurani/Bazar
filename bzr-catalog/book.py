from database import db, marshmallow, database_init


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False,)
    topic = db.Column(db.String(200), nullable=False,)
    quantity = db.Column(db.Integer, nullable=False, default=0,)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, title, topic, quantity, price):
        self.title = title
        self.quantity = quantity
        self.topic = topic
        self.price = price

    @classmethod
    def search(cls, topic):
        return Book.query.filter(Book.topic.ilike(f'%{topic}%'))

    @classmethod
    def get(cls, id):
        return Book.query.get(id)

    @classmethod
    def buy(cls, id):
        book = Book.query.get(id)
        if book is None:
            return book
        if book.quantity <= 0:
            raise cls.OutOfStockError()
        book.quantity -= 1
        db.session.commit()
        return book

    class OutOfStockError(Exception):
        pass


# Add the 4 books as an initial entry to the database
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
        fields = ('title', 'quantity', 'price')


book_lookup_schema = BookLookupSchema()
books_search_schema = BookSearchSchema(many=True)


