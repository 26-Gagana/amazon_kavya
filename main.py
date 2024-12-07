from flask import Flask, render_template, request, redirect, url_for, session
from models.models import db, Book, User
from werkzeug.security import generate_password_hash  # For password hashing

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management


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


# Route for Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


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


# Route for updating the quantity of a book in the cart
@app.route('/update_cart/<int:book_id>', methods=['POST'])
def update_cart(book_id):
    quantity = int(request.form.get('quantity'))

    # Find the book in the cart and update its quantity
    for book in session['cart']:
        if book['id'] == book_id:
            book['quantity'] = quantity
            break

    session.modified = True
    return redirect(url_for('cart'))


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


# Route for logging out
@app.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove the user session
    return redirect(url_for("login"))


# Run the app
if __name__ == "__main__":
    app.run(debug=True)