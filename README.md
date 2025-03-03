# DB_Security_Project
This project aims to create a secure database healthcare management system and aims to implement database security principle to create a enterprise level secure heathcare system.

# clone the repository
git clone git@github.com:stsh59/DB_Security_Project.git
cd DB_Security_Project

# Create and Activate a Virtual Environment
1. On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

3. On Windows:
python -m venv venv
venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Configuration
# Set Environment Variables

1. Flask settings
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

2. Database settings
DATABASE_URI=postgresql://username:password@localhost:5432/db_security_project

3. Additional environment variables (encryption keys, etc.)
ENCRYPTION_KEY=your_encryption_key_here

# Run the Flask Development Server:
flask run

