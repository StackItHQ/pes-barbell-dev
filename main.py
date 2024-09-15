import os
import gspread
import mysql.connector
import logging
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Google Sheets credentials
SERVICE_ACCOUNT_FILE = 'superjoin-435614-8fddc078511b.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Database credentials
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Google Sheets client setup
def get_google_sheets_service():
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client

# Fetch data from Google Sheets
def fetch_google_sheets_data():
    try:
        client = get_google_sheets_service()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        data = sheet.get_all_values()  # Get all values from the sheet
        logging.info("Fetched data from Google Sheets: %s", data)
        return data
    except Exception as e:
        logging.error("Error fetching data from Google Sheets: %s", e)
        raise

# Connect to MySQL database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=DB_USER,
            password=DB_PASSWORD,
            database="superjoin"
        )
        logging.info("Successfully connected to the database.")
        return conn
    except mysql.connector.Error as err:
        logging.error("Error connecting to the database: %s", err)
        raise

# Fetch data from the database
def fetch_database_data():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test")  # Replace with your actual query
        rows = cursor.fetchall()
        logging.info("Fetched data from database: %s", rows)
        return rows
    except mysql.connector.Error as err:
        logging.error("Error fetching data from database: %s", err)
        raise
    finally:
        cursor.close()
        conn.close()

# Insert data to MySQL database with auto-increment and timestamp
def insert_data_to_db(row):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "INSERT INTO test (column1, timeOfUpdate) VALUES (%s, %s)"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, (row[0], timestamp))
        conn.commit()
        logging.info("Data inserted into database with timestamp.")
    except mysql.connector.Error as err:
        logging.error("Error inserting data into database: %s", err)
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Insert data into Google Sheets
def insert_data_to_google_sheets(row):
    try:
        client = get_google_sheets_service()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        sheet.append_row(row)  # Append new row to Google Sheet
        logging.info("Data inserted into Google Sheets: %s", row)
    except Exception as e:
        logging.error("Error inserting data into Google Sheets: %s", e)

# Synchronize data between Google Sheets and database
def synchronize_data():
    try:
        # Fetch data from both sources
        google_sheets_data = fetch_google_sheets_data()
        db_data = fetch_database_data()

        # Convert data to sets for easier comparison
        google_sheets_set = {tuple(row) for row in google_sheets_data}
        print()
        print(google_sheets_data)
        db_set = {tuple(row[:1]) for row in db_data}  # Assuming you only want the first column to compare

        # Find missing data
        missing_in_db = google_sheets_set - db_set
        missing_in_sheet = db_set - google_sheets_set

        # Insert missing data into the database
        for row in missing_in_db:
            logging.info("Inserting into DB: %s", row)
            insert_data_to_db(row)

        # Insert missing data into Google Sheets
        for row in missing_in_sheet:
            logging.info("Inserting into Google Sheets: %s", row)
            insert_data_to_google_sheets(list(row))
    except Exception as e:
        logging.error("Error during synchronization: %s", e)

# Main synchronization process
if __name__ == "__main__":
    synchronize_data()
