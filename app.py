from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    image_filename = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    add_initial_data()
    print('Initialized the database.')

def add_initial_data():
    with app.app_context():
        # Create categories if they don't exist
        guppies = Category.query.filter_by(name='Guppies').first()
        if not guppies:
            guppies = Category(name='Guppies')
            db.session.add(guppies)

        koi = Category.query.filter_by(name='Koi').first()
        if not koi:
            koi = Category(name='Koi')
            db.session.add(koi)

        monster_fishes = Category.query.filter_by(name='Monster Fishes').first()
        if not monster_fishes:
            monster_fishes = Category(name='Monster Fishes')
            db.session.add(monster_fishes)

        # Add products
        # ... rest of the code ...

@app.route('/')
def home():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/category/<category_name>')
def show_category(category_name):
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return redirect(url_for('home'))
    return render_template('category.html', category=category)

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
    add_initial_data()
    app.run(debug=True, port=5002)
