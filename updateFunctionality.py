import logging
import gspread
import mysql.connector
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets and MySQL configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'superjoin-435614-8fddc078511b.json'
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Initialize credentials
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)

# Database connection
def connect_to_database():
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database="superjoin"
    )
    return conn

# Fetch Google Sheets row by row ID
def fetch_google_sheet_row_by_id(row_id):
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    data = sheet.get_all_values()
    for row in data:
        if row and len(row) > 1 and str(row[1]) == str(row_id):
            return row
    return None

# Fetch database row by ID
def fetch_db_row_by_id(row_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "SELECT * FROM test WHERE Id = %s"
    cursor.execute(query, (row_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# Update Google Sheets row
def update_google_sheet_row(row_id, column1):
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    data = sheet.get_all_values()
    for i, row in enumerate(data):
        print(i,row)
        if row and len(row) > 1 and str(row[1]) == str(row_id):
            sheet.update_cell(i+1, 1, column1)  # Update column1
            logging.info(f"Updated Google Sheets row {i + 1} with new value: {column1}")
            return True
    return False

# Update database row
def update_db_row(row_id, column1):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "UPDATE test SET column1 = %s WHERE Id = %s"
    cursor.execute(query, (column1, row_id))
    conn.commit()
    conn.close()
    logging.info(f"Updated database row with ID {row_id} with new value: {column1}")

# Sync updates between Google Sheets and the database
def sync_updates(prev_sheet_data, current_sheet_data, prev_db_data, current_db_data):
    logging.info("Checking for updates between Google Sheets and database...")

    # Check for changes in Google Sheets (compared to previous data)
    for current_row in current_sheet_data:
        if current_row and len(current_row) > 1:
            row_id = current_row[1]  # Assuming ID is in column 2
            matching_db_row = fetch_db_row_by_id(row_id)
            if matching_db_row:
                if current_row[0] != matching_db_row[0]:  # column1 mismatch
                    logging.info(f"Discrepancy detected: Google Sheets row {current_row} does not match DB row {matching_db_row}")
                    update_db_row(row_id, current_row[0])  # Update DB with Google Sheets value

    # Check for changes in the database (compared to previous data)
    for current_db_row in current_db_data:
        if current_db_row:
            row_id = current_db_row[1]  # Assuming ID is in column 2
            matching_sheet_row = fetch_google_sheet_row_by_id(row_id)
            if matching_sheet_row:
                if current_db_row[0] != matching_sheet_row[0]:  # column1 mismatch
                    logging.info(f"Discrepancy detected: DB row {current_db_row} does not match Google Sheets row {matching_sheet_row}")
                    update_google_sheet_row(row_id, current_db_row[0])  # Update Google Sheets with DB value