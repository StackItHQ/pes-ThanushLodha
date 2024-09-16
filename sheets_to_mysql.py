import gspread
from google.oauth2.service_account import Credentials
import pymysql
import sys
from dotenv import load_dotenv
import os
load_dotenv()

SCOPES = os.getenv("SCOPES").split(",")
CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
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

def authenticate_google_sheets():
    """Authenticate with Google Sheets API and return the client."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def connect_to_mysql():
    """Connect to MySQL and return the connection and cursor."""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    return conn, cursor

def create_log_table(cursor):
    """Create a log table for tracking changes."""
    create_log_table_query = """
    CREATE TABLE IF NOT EXISTS log_table (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        table_name VARCHAR(255) NOT NULL,
        row_id INT NOT NULL
    );
    """
    cursor.execute(create_log_table_query)
    print("Log table created or already exists.")

def update_global_variable(cursor, value):
    """Update the global variable in the database."""
    update_query = "UPDATE global_variables SET value = %s WHERE variable_name = 'sheets';"
    cursor.execute(update_query, (value,))
    print(f"Updated 'sheets' value to {value}.")

def create_table(cursor, table_name, columns):
    """Create a table in MySQL."""
    columns_str = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
    cursor.execute(create_table_query)
    print(f"Table {table_name} created or already exists.")

def insert_data(cursor, table_name, columns, rows):
    """Insert data into the MySQL table."""
    for i in range(1, len(rows)):  
        row_number = i
        row_values = [row_number] + rows[i]
        
        placeholders = ", ".join(["%s"] * len(row_values))
        update_clause = ", ".join([f"{col_name} = VALUES({col_name})" for col_name, _ in columns[1:]])
        
        insert_query = f"""
        INSERT INTO {table_name} VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """
        
        cursor.execute(insert_query, row_values)
    print(f"Data inserted into {table_name}.")

def create_triggers(cursor, table_name,conn):
    """Create triggers for INSERT, UPDATE, and DELETE operations."""
    insert_trigger_query = f"""
    CREATE TRIGGER after_insert_{table_name.replace('`', '')}
    AFTER INSERT ON {table_name}
    FOR EACH ROW
    BEGIN
        DECLARE sheets_value INT;
        SELECT value INTO sheets_value FROM global_variables WHERE variable_name = 'sheets';
        IF sheets_value = 1 THEN
            INSERT INTO log_table (table_name, row_id) VALUES ('{table_name.replace('`', '')}', NEW.ROW_ID);
        END IF;
    END;
    """

    update_trigger_query = f"""
    CREATE TRIGGER after_update_{table_name.replace('`', '')}
    AFTER UPDATE ON {table_name}
    FOR EACH ROW
    BEGIN
        DECLARE sheets_value INT;
        SELECT value INTO sheets_value FROM global_variables WHERE variable_name = 'sheets';
        IF sheets_value = 1 THEN
            INSERT INTO log_table (table_name, row_id) VALUES ('{table_name.replace('`', '')}', NEW.ROW_ID);
        END IF;
    END;
    """

    delete_trigger_query = f"""
        CREATE TRIGGER after_delete_{table_name.replace('`', '')}
        AFTER DELETE ON {table_name}
        FOR EACH ROW
        BEGIN
            DECLARE sheets_value INT;
            SELECT value INTO sheets_value FROM global_variables WHERE variable_name = 'sheets';
            
            IF sheets_value = 1 THEN
                INSERT INTO log_table (table_name, row_id) 
                VALUES ('{table_name.replace('`', '')}', OLD.ROW_ID);
                INSERT INTO {table_name} (ROW_ID) 
                VALUES (OLD.ROW_ID);
            END IF;
        END;
        """
    
    cursor.execute(insert_trigger_query)
    cursor.execute(update_trigger_query)
    cursor.execute(delete_trigger_query)
    conn.commit()
    print(f"Triggers for INSERT, UPDATE, and DELETE created for {table_name}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <Google Sheets URL>")
        sys.exit(1)
    
    sheets_url = sys.argv[1]
    
    client = authenticate_google_sheets()
    conn, cursor = connect_to_mysql()
    
    create_log_table(cursor)
    update_global_variable(cursor, 0)
    
    sheet = client.open_by_url(sheets_url)
    
    for sheets in sheet.worksheets():
        print(f"Processing sheet: {sheets.title}")
        rows = sheets.get_all_values()
        
        if len(rows) == 0:
            print(f"Skipping empty sheet: {sheets.title}")
            continue
        
        values_list = rows[0]
        columns = [(f'`{col}`' if col else f'`Col{chr(65 + i)}`', 'VARCHAR(255)') for i, col in enumerate(values_list)]
        columns.insert(0, ('`ROW_ID`', 'INT PRIMARY KEY'))
        
        table_name = f"`{sheet._properties['title']}_{sheets.title}`".replace(" ", "_")
        
        create_table(cursor, table_name, columns)
        insert_data(cursor, table_name, columns, rows)
        create_triggers(cursor, table_name,conn)
        
        conn.commit()
    
    update_global_variable(cursor, 1)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()