import os
import gspread
import mysql.connector
import logging
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Import the update sync logic from edits.py
from edits import fetch_db_row_by_id, sync_updates, update_db_row

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
def sync_sheets_and_db(prev_sheet_data, prev_db_data):
    current_sheet_data = fetch_google_sheets_data()
    current_db_data = fetch_db_data()

    dbChange = False
    sheetChange = False

    # Detect and sync insertions and updates from Google Sheets to DB
    for row in current_sheet_data:
        if row and row[0].strip():
            column1 = row[0].strip()
            row_id = row[1] if len(row) > 1 else None

            if row_id:
                # This is an existing row, check for updates
                db_row = fetch_db_row_by_id(row_id)
                if db_row and db_row[0] != column1:
                    # Update the existing row in the database
                    update_db_row(row_id, column1)
                    logging.info(f"Updated row in DB: ID {row_id}, new value: {column1}")
                    dbChange = True
            else:
                # This is a new row, insert it
                new_row_id = insert_to_database(column1)
                logging.info(f"New row in Google Sheets detected: {row}. Inserted into DB with ID {new_row_id}")
                # Update the Google Sheet with the new ID
                sheet = client.open_by_key(SPREADSHEET_ID).sheet1
                cell = sheet.find(column1)
                if cell:
                    row_number = cell.row
                    sheet.update_cell(row_number, 2, new_row_id)
                    dbChange = True

    # Handle deletions from Google Sheets to DB
    if not dbChange:
        for prev_row in prev_sheet_data:
            if prev_row not in current_sheet_data:
                row_id = prev_row[1]
                delete_from_database(row_id)
                logging.info(f"Row deleted from Google Sheets: {prev_row}. Deleted from DB")
                dbChange = True
        
    # Detect and sync insertions from DB to Google Sheets
    for row in current_db_data:
        if row not in prev_db_data:  # New row detected in DB
            column1 = row[0].strip()
            row_id = row[1]
            if column1:  # Only add rows with non-empty column1 to Google Sheets
                insert_to_google_sheets(column1, row_id)
                logging.info(f"New row in DB detected: {row}. Added to Google Sheets")
                sheetChange = True
    
    # Handle deletions from DB to Google Sheets
    if not sheetChange:
        for prev_row in prev_db_data:
            if prev_row not in current_db_data:  # Row deleted from DB
                row_id = prev_row[1]
                sheet = client.open_by_key(SPREADSHEET_ID).sheet1
                cell = sheet.find(str(row_id))  # Find the row with the ID
                if cell:
                    row_number = cell.row
                    delete_from_google_sheets(row_number)
                    logging.info(f"Row deleted from DB: {prev_row}. Deleted from Google Sheets")
                    sheetChange = True

    # Handle updates (delegated to edits.py) only if there are no inserts/deletes
    if not dbChange and not sheetChange:
        sync_updates(prev_sheet_data, current_sheet_data, prev_db_data, current_db_data)

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