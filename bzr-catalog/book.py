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
    def update(cls, id, title=None, quantity=None, topic=None, price=None):
        book = Book.query.get(id)
        if book is None:
            return None
        book.title = title if title is not None else book.title
        book.quantity = quantity if quantity is not None else book.quantity
        book.topic = topic if topic is not None else book.topic
        book.price = price if price is not None else book.price

        db.session.commit()
        return book


# Add the 4 books as an initial entry to the database
database_init += [
    Book('How to get a good grade in DOS in 20 minutes a day', 'Distributed Systems', 10, 25.00),
    Book('RPCs for Dummies', 'Distributed Systems', 5, 50.00),
    Book('Xen and the Art of Surviving Graduate School', 'Graduate School', 10, 15.00),
    Book('Cooking for the Impatient Graduate Student', 'Graduate School', 25, 10.00)
]


class TopicSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title')


class ItemSchema(marshmallow.Schema):
    class Meta:
        fields = ('title', 'quantity', 'price')


class UpdateSchema(marshmallow.Schema):
    class Meta:
        fields = ('title', 'quantity', 'topic', 'price')


item_schema = ItemSchema()
topic_schema = TopicSchema(many=True)
update_schema = UpdateSchema()


