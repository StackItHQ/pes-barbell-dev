# import os
# import gspread
# from oauth2client.client import OAuth2WebServerFlow
# from oauth2client.file import Storage
# from oauth2client import tools
# import mysql.connector
# import logging
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # OAuth2 client configuration from environment variables
# CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
# CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
# SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# TOKEN_FILE = 'token.json'
# SERVICE_ACCOUNT_FILE = 'superjoin-435614-8fddc078511b.json'

# # Set up logging
# logging.basicConfig(level=logging.INFO)

# def get_google_sheets_service():
#     flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
#                                client_secret=CLIENT_SECRET,
#                                scope=SCOPE,
#                                redirect_uri=REDIRECT_URI)

#     storage = Storage(TOKEN_FILE)
#     credentials = storage.get()

#     if credentials is None or credentials.invalid:
#         credentials = tools.run_flow(flow, storage)
    
#     client = gspread.authorize(credentials)
#     return client

# def fetch_google_sheets_data():
#     try:
#         client = get_google_sheets_service()
#         sheet = client.open_by_key(os.getenv('SPREADSHEET_ID')).sheet1
#         data = sheet.get_all_values()
#         logging.info("Fetched data from Google Sheets: %s", data)
#         return data
#     except Exception as e:
#         logging.error("Error fetching data from Google Sheets: %s", e)
#         raise

# def connect_to_database():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             user=os.getenv('DB_USER'),
#             password=os.getenv('DB_PASSWORD'),
#             database="superjoin"
#         )
#         logging.info("Successfully connected to the database.")
#         return conn
#     except mysql.connector.Error as err:
#         logging.error("Error connecting to the database: %s", err)
#         raise

# def insert_data_to_db(data):
#     try:
#         conn = connect_to_database()
#         cursor = conn.cursor()
#         query = "INSERT INTO test (column1) VALUES (%s)"
#         print(data)
#         for row in data:
#             if len(row) == 2:
#                 values = (row[1],)
#                 logging.info("Inserting values: %s", values)
#                 cursor.execute(query, values)
        
#         conn.commit()
#         logging.info("Data successfully inserted into the database.")
#     except mysql.connector.Error as err:
#         logging.error("Error inserting data into database: %s", err)
#         conn.rollback()
#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()
#             logging.info("Database connection closed.")

# def main():
#     try:
#         google_sheets_data = fetch_google_sheets_data()
#         insert_data_to_db(google_sheets_data)
#     except Exception as e:
#         logging.error("An error occurred during the main process: %s", e)

# if __name__ == "__main__":
#     main()

import os
import gspread
from google.oauth2 import service_account
import mysql.connector
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SERVICE_ACCOUNT_FILE = 'superjoin-435614-8fddc078511b.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_google_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client

def fetch_google_sheets_data():
    try:
        client = get_google_sheets_service()
        sheet = client.open_by_key(os.getenv('SPREADSHEET_ID')).sheet1
        data = sheet.get_all_values()
        logging.info("Fetched data from Google Sheets: %s", data)
        return data
    except Exception as e:
        logging.error("Error fetching data from Google Sheets: %s", e)
        raise

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database="superjoin"
        )
        logging.info("Successfully connected to the database.")
        return conn
    except mysql.connector.Error as err:
        logging.error("Error connecting to the database: %s", err)
        raise

def insert_data_to_db(data):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "INSERT INTO test (column1) VALUES (%s)"
        print(data)
        for row in data:
            if len(row) == 2:
                values = (row[1],)
                logging.info("Inserting values: %s", values)
                cursor.execute(query, values)
        
        conn.commit()
        logging.info("Data successfully inserted into the database.")
    except mysql.connector.Error as err:
        logging.error("Error inserting data into database: %s", err)
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")

def main():
    try:
        google_sheets_data = fetch_google_sheets_data()
        insert_data_to_db(google_sheets_data)
    except Exception as e:
        logging.error("An error occurred during the main process: %s", e)

if __name__ == "__main__":
    main()
