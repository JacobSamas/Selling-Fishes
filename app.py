from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)

# Set a strong, secret key for session management
app.secret_key = 'your_secret_key'

# Configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with your Flask app
db = SQLAlchemy(app)

# Initialize Flask-Migrate with your Flask app and SQLAlchemy database
migrate = Migrate(app, db)

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    image_filename = db.Column(db.String(200))  # Add this line for the image filename

    def __repr__(self):
        return f'<Product {self.name}>'


# Create the database tables
with app.app_context():
    db.create_all()

# Add your routes here
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/guppies')
def guppies():
    return render_template('guppies.html')

@app.route('/koi')
def koi():
    return render_template('koi.html')

@app.route('/monster_fishes')
def monster_fishes():
    return render_template('monster_fishes.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    fish_id = request.form.get('fish_id')
    if 'cart' not in session:
        session['cart'] = []  # Initialize an empty cart if it doesn't exist
    print("Appending", fish_id)
    session['cart'].append(fish_id)  # Add the fish ID to the cart
    session.modified = True  # Mark the session as modified to ensure it gets saved
    return redirect(url_for('home'))  # Redirect to the home page after adding to cart

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
