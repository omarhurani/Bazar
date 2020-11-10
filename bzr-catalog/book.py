from database import db, marshmallow


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


class BookBriefSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title', 'topic')


class BookSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title', 'topic', 'quantity', 'cost')


book_schema = BookSchema(strict=True)
books_schema = BookBriefSchema(many=True, strict=True)
