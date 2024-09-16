import time
import pymysql
from dotenv import load_dotenv
import os
import gspread
from google.oauth2.service_account import Credentials
import re

load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(os.getenv('GOOGLE_SHEETS_CREDENTIALS'), scopes=scopes)
client = gspread.authorize(creds)

DB_CONFIG = {
    "charset": "utf8mb4",
    "connect_timeout": 10,
    "cursorclass": pymysql.cursors.DictCursor,
    "db": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "password": os.getenv("DB_PASSWORD"),
    "read_timeout": 10,
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "write_timeout": 10,
}

def sync_table_with_sheet(table_name, row_id):
    try:
        sheet_name = os.getenv('GOOGLE_SHEET_URL')
        sheet = client.open_by_url(sheet_name)

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name} WHERE ROW_ID = %s", (row_id,))
        row = cursor.fetchone()

        if not row:
            print(f"No data found for ROW_NUMBER {row_id} in table {table_name}")
            return

        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column["Field"] for column in cursor.fetchall()[1:]]
        columns = ["" if re.match(r"Col[A-Z]", col) else col for col in columns]

        for worksheet in sheet.worksheets():
            if worksheet.title == table_name.split('_')[-1]:
                row_values = list(row.values())[1:]
                worksheet.update(f"A{row_id+1}", [row_values])
                print(f"Synced row {row_id} of table {table_name} with Google Sheet {worksheet.title}")
                return
    except Exception as e:
        print(f"Error syncing table {table_name} and row {row_id} with Google Sheets: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def monitor_log_table():
    try:
        while True:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()

            cursor.execute("SELECT log_id, table_name, row_id FROM log_table")
            logs = cursor.fetchall()
            print(logs)
            if logs:
                for log in logs:
                    log_id, table_name, row_id = log["log_id"], log["table_name"], log["row_id"]
                    sync_table_with_sheet(table_name, row_id)
                    cursor.execute(f"DELETE FROM log_table WHERE log_id = %s", (log_id,))
                    conn.commit()
                    print(f"Processed log for table {table_name}, row {row_id}, and removed log entry with ID {log_id}")

            cursor.close()
            conn.close()

            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping log monitoring.")
    except Exception as e:
        print(f"Error while monitoring log table: {str(e)}")

if __name__ == "__main__":
    monitor_log_table()
