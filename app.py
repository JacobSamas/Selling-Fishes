from flask import Flask, render_template, session, redirect, url_for, request

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = 'your_secret_key'  # Set a strong, secret key for session management

@app.route('/')
def home():
    return render_template('index.html')

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
    app.run(debug=False, port=5002)
