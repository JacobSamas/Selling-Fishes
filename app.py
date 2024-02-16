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
    image_filename = db.Column(db.String(200), nullable=True)
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
        db.create_all()  # Create tables if they don't exist

        # Categories with their images
        categories_data = [
            ('Guppies', 'guppies.jpg'),
            ('Koi', 'koi.jpg'),
            ('Monster Fishes', 'monster_fishes.jpg')
        ]

        # Iterate through categories_data to add categories to the database
        for name, image_filename in categories_data:
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name, image_filename=image_filename)
                db.session.add(category)

        # ... code to add products ...
        products_data = [
            ('Albino Red Guppy',5.99, 'A vibrant red guppy.', 'albino_red_guppy.jpg', 'Guppies'),
            ('Albino White Guppy', 6.49, 'A pure white, elegant guppy.', 'albino_white_guppy.jpg', 'Guppies'),
            ('Purple Berry Guppy', 7.99, 'A striking purple colored guppy.', 'purple_berry_guppy.jpg', 'Guppies'),
            ('Gold Guppy', 8.99, 'A shiny gold guppy, very eye-catching.', 'gold_guppy.jpg', 'Guppies'),
            ('Japanese Koi', 20.99, 'Elegant and traditional Japanese Koi.', 'japanese_koi.jpg', 'Koi'),
            ('Butterfly Koi', 25.99, 'Long-finned, graceful Butterfly Koi.', 'butterfly_koi.jpg', 'Koi'),
            ('Regular Koi', 18.99, 'Beautifully patterned Regular Koi.', 'regular_koi.jpg', 'Koi'),
            ('Alligator Gar', 50.00, 'A large, predatory fish resembling an alligator.', 'alligator_gar.jpg', 'Monster Fishes'),
            ('Oscar', 30.00, 'A popular aquarium fish with a vibrant personality.', 'oscar.jpg', 'Monster Fishes'),
            ('Arowana', 80.00, 'Often called the "dragon fish", known for its shiny scales.', 'arowana.jpg', 'Monster Fishes'),
            ('Piranha', 20.00, 'Famous for its sharp teeth and powerful jaws.', 'piranha.jpg', 'Monster Fishes')
            # Add more products for each category...
        ]
        for name, price, description, image_filename, category_name in products_data:
            category = Category.query.filter_by(name=category_name).first()
            product = Product(name=name, price=price, description=description, image_filename=image_filename, category=category)
            db.session.add(product)

        db.session.commit()

@app.route('/')
def home():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/category/<category_name>')
def show_category(category_name):
    category = Category.query.filter_by(name=category_name).first_or_404()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, products=products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))  # Default to 1 if not provided

    if 'cart' not in session:
        session['cart'] = {}  # Initialize an empty cart if it doesn't exist

    if product_id in session['cart']:
        session['cart'][product_id] += quantity  # Increase quantity if product already in cart
    else:
        session['cart'][product_id] = quantity  # Add new product to the cart

    session.modified = True  # Mark the session as modified to ensure it gets saved
    return redirect(url_for('home'))  # Redirect to the home page after adding to cart


@app.route('/cart')
def cart():
    cart_items = []
    total_price = 0

    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product:
                total_price += product.price * quantity
                cart_items.append({'product': product, 'quantity': quantity})

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


if __name__ == '__main__':
    add_initial_data()
    app.run(debug=True, port=5002)
