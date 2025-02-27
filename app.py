from flask import Flask, render_template, g, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from extensions import db, bcrypt, login_manager, jwt
from flask_jwt_extended import JWTManager  # Import JWTManager
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp  # ✅ Added Reports Blueprint
from routes.billing import billing_bp
from routes.patients import patients_bp
from models import User, Role, Patient, RolePermission, reflect_fhir_tables
from utils import check_permission  # 导入 check_permission
import secrets
from urllib.parse import quote_plus

from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 读取加密密钥
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
# 打印密钥（用于调试）
print(f"Encryption Key: {ENCRYPTION_KEY}")

# Initialize Flask app

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure random secret key

# Encode the password to handle special characters in MySQL password
password = quote_plus("123456")  # Encodes '@' in password
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/visualization'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # JWT secret key

# In app.py, after setting JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # ✅ Look for JWT in cookies
app.config['JWT_COOKIE_SECURE'] = True  # For HTTPS only
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # ✅ Disable CSRF for simplicity (enable in production)
app.config['JWT_SESSION_COOKIE'] = False  # Use standard cookie settings

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Initialize JWTManager properly
jwt = JWTManager(app)

# Ensure FHIR tables are reflected **inside the app context**
with app.app_context():
    reflect_fhir_tables()  # ✅ Load FHIR tables dynamically
    db.create_all()  # ✅ Creates tables if not already present

# Flask-Login user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Fetch user by ID from the database

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')       # Authentication routes
app.register_blueprint(admin_bp, url_prefix='/admin')     # Admin management routes
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')  # Dashboard routes
app.register_blueprint(reports_bp, url_prefix='/reports')  # Reports related routes
app.register_blueprint(billing_bp, url_prefix='/billing')  # Billing related routes
app.register_blueprint(patients_bp, url_prefix='/patients')

# Define check_permission as a context processor
@app.context_processor
def utility_processor():
    return dict(check_permission=check_permission)  # 使用 utils.py 中的 check_permission

# Define home route
@app.route('/')
def home():
    return render_template('home.html', title="Home")

if __name__ == '__main__':
    app.run(debug=True)