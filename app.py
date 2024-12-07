from flask import Flask, render_template, request, redirect, url_for, session, flash, json
from models.models import db, Book, User, Cart
from werkzeug.security import generate_password_hash
import plotly.graph_objects as go
import plotly
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amazon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


# Route for Home Page
@app.route("/")
def home():
    return render_template("home.html")


# Route for Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user exists in the database and validate the password
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials, please try again."
    return render_template("login.html")


# Route for Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)  # Hash the password

        # Create a new user and add it to the database
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))  # Redirect to login page after registration
    return render_template("register.html")


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        image_url = request.form['image_url']

        new_book = Book(name=name, price=price, image_url=image_url)
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))

    # Fetch all books to display in the table
    books = Book.query.all()
    return render_template('add_book.html', books=books)


@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book.name = request.form['name']
        book.price = float(request.form['price'])
        book.image_url = request.form['image_url']

        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('add_book'))

    return render_template('edit_book.html', book=book)


@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('add_book'))


@app.route('/confirm-delete-book/<int:book_id>', methods=['GET', 'POST'])
def confirm_delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        # Delete the book
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
        return redirect(url_for('add_book'))

    return render_template('delete.html', book=book)


# Route for Dashboard
# Route for Dashboard
@app.route("/dashboard")
def dashboard():
    books = Book.query.all()  # Fetch all books from the database
    return render_template("dashboard.html", books=books)  # Pass books to the template



# Route for displaying the cart
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        # Adding a new book to the cart
        book_title = request.form.get('book_title')
        book_price = float(request.form.get('book_price'))
        book_id = len(session['cart']) + 1

        new_book = {
            'id': book_id,
            'title': book_title,
            'price': book_price,
            'quantity': 1
        }

        # Add new book to the cart
        session['cart'].append(new_book)
        session.modified = True  # Ensure the session is modified

    return render_template('cart.html', cart=session['cart'])


@app.route('/add-to-cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))

    # Check if the book exists
    book = Book.query.get_or_404(book_id)

    # Check if the item is already in the cart
    cart_item = Cart.query.filter_by(user_id=user_id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=user_id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{book.name} has been added to your cart!', 'success')
    return redirect(url_for('dashboard'))



@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        flash('Please log in to view your cart.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return render_template('cart.html', cart_items=cart_items)




# Route for updating the quantity of a book in the cart
@app.route('/update-cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    quantity = int(request.form.get('quantity'))
    cart_item.quantity = quantity
    db.session.commit()
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('view_cart'))



# Route for removing a book from the cart
@app.route('/remove_item/<int:book_id>', methods=['GET'])
def remove_item(book_id):
    session['cart'] = [book for book in session['cart'] if book['id'] != book_id]
    session.modified = True
    return redirect(url_for('cart'))


# Route for checking out (optional)
@app.route('/checkout')
def checkout():
    if 'cart' not in session or len(session['cart']) == 0:
        return redirect(url_for('cart'))

    return render_template('checkout.html', cart=session['cart'])

@app.route("/analysis")
def analysis():
    # Query the database to get all books and their prices
    books = Book.query.all()

    # Extract book names and prices
    book_names = [book.name for book in books]
    book_prices = [book.price for book in books]

    # Create a Plotly bar chart
    fig = go.Figure(data=[go.Bar(
        x=book_names,
        y=book_prices,
        marker_color='orange'
    )])

    # Update layout of the graph
    fig.update_layout(
        title="Book Prices",
        xaxis_title="Book Name",
        yaxis_title="Price ($)",
        template="plotly_dark"
    )

    # Convert the plot to JSON to send to the template
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("analysis.html", graph_json=graph_json)


# Route for logging out
@app.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove the user session
    return redirect(url_for("login"))


# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)