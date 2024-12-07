from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'  # Correct table name declaration

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"


# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Book {self.name}>"


# Cart Model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)  # Foreign key for Book
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key for User
    quantity = db.Column(db.Integer, nullable=False)

    # Relationships
    book = db.relationship('Book', backref='cart_entries', lazy=True)
    user = db.relationship('User', backref='cart_entries', lazy=True)

    def __repr__(self):
        return f"<Cart {self.id}, Book {self.book.name}, User {self.user.email}>"
