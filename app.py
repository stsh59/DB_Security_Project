from flask import Flask, render_template
import secrets
from urllib.parse import quote_plus
from extensions import db, bcrypt, login_manager
from routes import auth, admin, dashboard, reports
from models import User  # Import User model

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key

# Encode the password to handle special characters
password = quote_plus("9808311242Ab@")  # Encodes the '@' character
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/hospitaldb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Define the user_loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Fetch user by ID from the database

# Register Blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(reports.bp)

# Define a home route
@app.route('/')
def home():
    return render_template('base.html', title="Home")

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if not already present
    app.run(debug=True)
