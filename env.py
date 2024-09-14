import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define environment variables
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
