import os
import gspread
import mysql.connector
import logging
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

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

# Fetch data from Google Sheets
def fetch_google_sheets_data():
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet.get_all_values()

# Fetch data from the database
def fetch_db_data():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test")
    data = cursor.fetchall()
    conn.close()
    return data

# Insert into database
def insert_to_database(column1):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "INSERT INTO test (column1) VALUES (%s)"
    cursor.execute(query, (column1,))
    conn.commit()
    row_id = cursor.lastrowid  # Get the auto-incremented ID
    conn.close()
    return row_id

# Delete from database
def delete_from_database(row_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "DELETE FROM test WHERE Id = %s"
    cursor.execute(query, (row_id,))
    conn.commit()
    conn.close()

# Insert into Google Sheets
def insert_to_google_sheets(column1, row_id):
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    formatted_row = [column1, row_id]
    logging.info(f"Inserting into Google Sheets: {formatted_row}")
    sheet.append_row(formatted_row)

# Delete from Google Sheets
def delete_from_google_sheets(row_index):
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    logging.info(f"Deleting from Google Sheets: Row {row_index}")
    sheet.delete_rows(row_index)

# Sync logic
def sync_sheets_and_db(prev_sheet_data, prev_db_data):
    current_sheet_data = fetch_google_sheets_data()
    current_db_data = fetch_db_data()

    # Detect and sync changes from Google Sheets to DB
    for row in current_sheet_data:
        if row not in prev_sheet_data:  # New row detected in Sheets
            column1 = row[0]
            row_id = insert_to_database(column1)
            logging.info(f"New row in Google Sheets detected: {row}. Inserted into DB with ID {row_id}")
            # Update the Google Sheet with the new ID
            sheet = client.open_by_key(SPREADSHEET_ID).sheet1
            cell = sheet.find(column1)  # Find the row with the new column1 value
            if cell:
                row_number = cell.row
                sheet.update_cell(row_number, 2, row_id)  # Update the ID column

    for prev_row in prev_sheet_data:
        if prev_row not in current_sheet_data:  # Row deleted from Sheets
            row_id = prev_row[1]  # Assuming ID is in column 2
            delete_from_database(row_id)
            logging.info(f"Row deleted from Google Sheets: {prev_row}. Deleted from DB")

    # Detect and sync changes from DB to Google Sheets
    for row in current_db_data:
        if row not in prev_db_data:  # New row detected in DB
            column1 = row[0]
            row_id = row[1]
            row_to_add = [column1, row_id]
            insert_to_google_sheets(column1, row_id)
            logging.info(f"New row in DB detected: {row}. Added to Google Sheets")

    for prev_row in prev_db_data:
        if prev_row not in current_db_data:  # Row deleted from DB
            row_id = prev_row[0]
            sheet = client.open_by_key(SPREADSHEET_ID).sheet1
            cell = sheet.find(str(row_id))  # Find the row with the ID
            if cell:
                row_number = cell.row
                delete_from_google_sheets(row_number)
                logging.info(f"Row deleted from DB: {prev_row}. Deleted from Google Sheets")

# Main sync loop
def sync_loop():
    prev_sheet_data = fetch_google_sheets_data()
    prev_db_data = fetch_db_data()

    while True:
        sync_sheets_and_db(prev_sheet_data, prev_db_data)

        # Update the previous state
        prev_sheet_data = fetch_google_sheets_data()
        prev_db_data = fetch_db_data()

        time.sleep(10)  # Check for changes every 10 seconds

if __name__ == "__main__":
    logging.info("Starting sync loop")
    sync_loop()
