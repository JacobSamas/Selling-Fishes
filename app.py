from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions import db, login_manager
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


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
            ('Albino Red Guppy', 5.99, 'A vibrant red guppy.', 'albino_red_guppy.jpg', 'Guppies'),
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
            if category:
                product = Product.query.filter_by(name=name, category=category).first()
                if not product:
                    product = Product(name=name, price=price, description=description, image_filename=image_filename, category=category)
                    db.session.add(product)

        db.session.commit()

@app.route('/')
def home():
    categories = Category.query.all()
    
    # Initialize an empty cart summary
    cart_summary = {'total_items': 0, 'total_price': 0.0}
    
    # Populate the cart summary if there are items in the cart
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product:
                cart_summary['total_items'] += quantity
                cart_summary['total_price'] += product.price * quantity

    # Pass the cart summary to the template
    return render_template('index.html', categories=categories, cart_summary=cart_summary)


@app.route('/category/<category_name>')
def show_category(category_name):
    sort = request.args.get('sort', 'recommended')

    category = Category.query.filter_by(name=category_name).first_or_404()
    
    if sort == 'price_asc':
        products = Product.query.filter_by(category_id=category.id).order_by(Product.price.asc()).all()
    elif sort == 'price_desc':
        products = Product.query.filter_by(category_id=category.id).order_by(Product.price.desc()).all()
    elif sort == 'alphabetical':
        products = Product.query.filter_by(category_id=category.id).order_by(Product.name).all()
    else:  # recommended or default case
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
    total_price = 0.0  # Ensure this is initialized to a float

    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product:
                total_price += product.price * quantity
                cart_items.append({'product': product, 'quantity': quantity})

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if 'cart' in session and product_id in session['cart']:
        if quantity > 0:
            session['cart'][product_id] = quantity
        else:
            del session['cart'][product_id]

    session.modified = True
    return redirect(url_for('cart'))


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    # Adding more detailed logging for debugging
    print("Current session cart before removal:", session.get('cart'),  flush=True)

    product_id = request.form.get('product_id')
    print("Product ID to remove:", product_id, file=sys.stdout)

    if not product_id:
        print("No product ID provided", file=sys.stdout)
        return redirect(url_for('cart'))

    if product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True
        print("Product removed, updated session cart:", session.get('cart'), file=sys.stdout)
    else:
        print(f"Product ID {product_id} not in cart", file=sys.stdout)

    return redirect(url_for('cart'))


@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    # Example search logic: find products matching the query
    results = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('search_results.html', results=results)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/orders')
def orders():
    # Logic to retrieve and display user's orders
    return render_template('orders.html')

@app.route('/wishlist')
def wishlist():
    # Logic to retrieve and display user's wishlist
    return render_template('wishlist.html')

@app.route('/account')
def account():
    # Logic to display user account details
    return render_template('account.html')


# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

if __name__ == '__main__':
    from models import User, Category, Product
    from auth import auth

    # initdb_command()

    app.register_blueprint(auth, url_prefix='/auth')

    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5002)
