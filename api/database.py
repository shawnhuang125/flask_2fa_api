import mysql.connector
from api.config import Config
import os
import datetime
import pandas as pd

# Set upload and save folders
UPLOAD_FOLDER_CSV = os.path.join(os.getcwd(), 'upload_csv')
UPLOAD_FOLDER_SQL = os.path.join(os.getcwd(), 'upload_sql')

# Ensure /upload_csv and /upload_sql folders exist
os.makedirs(UPLOAD_FOLDER_CSV, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SQL, exist_ok=True)

def get_db_connection():
    """
    Establish a database connection and return the connection object or an error message.
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        print("Successfully connected to the database")
        return conn, None
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None, f"Database connection failed: {err}"

def escape_sql_string(value):
    """
    Escape special characters in SQL strings to prevent syntax errors.
    """
    if pd.isnull(value) or value == '':
        return 'NULL'
    if isinstance(value, str):
        value = value.replace("'", "''")  # Handle single quotes
        value = value.replace("\\", "\\\\")  # Handle backslashes
        value = value.replace("\n", " ").replace("\r", " ")  # Handle newlines
        return f"'{value.strip()}'"
    return value

def convert_csv_to_sql(file_path, output_folder=UPLOAD_FOLDER_SQL):
    """
    Convert a CSV file to an SQL script file and save it to the specified folder.
    """
    try:
        df = pd.read_csv(file_path)

        # Validate required columns in the CSV file
        expected_columns = ['name', 'address', 'phone', 'rating', 'opening_hours', 'review_author', 'review_rating', 'review_text']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV file is missing required columns: {', '.join(missing_columns)}")
        
        # Generate table name and SQL file name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = "places_reviews"

        create_table_sql = f'''
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            address TEXT,
            phone VARCHAR(50),
            rating DECIMAL(2,1),
            opening_hours TEXT,
            review_author VARCHAR(255),
            review_rating INT,
            review_text TEXT
        );
        '''

        insert_statements = []
        for _, row in df.iterrows():
            values = (
                escape_sql_string(row['name']),
                escape_sql_string(row['address']),
                escape_sql_string(row['phone']),
                row['rating'] if pd.notnull(row['rating']) else 'NULL',
                escape_sql_string(row['opening_hours']),
                escape_sql_string(row['review_author']),
                row['review_rating'] if pd.notnull(row['review_rating']) else 'NULL',
                escape_sql_string(row['review_text'])
            )

            insert_query = f'''
            INSERT INTO `{table_name}` 
            (name, address, phone, rating, opening_hours, review_author, review_rating, review_text) 
            VALUES ({', '.join(map(str, values))});
            '''
            insert_statements.append(insert_query)

        # Save SQL script to the specified folder
        sql_file_name = f"{table_name}_{timestamp}.sql"
        sql_file_path = os.path.join(output_folder, sql_file_name)
        with open(sql_file_path, "w", encoding="utf-8") as sql_file:
            sql_file.write(create_table_sql + "\n")
            sql_file.write("\n".join(insert_statements))

        print(f"SQL file successfully saved to {sql_file_path}")
        return sql_file_path

    except Exception as e:
        print(f"CSV conversion failed: {e}")
        raise

def import_sql_to_db(sql_file_path):
    """
    Import an SQL script file into the database.
    """
    if not os.path.exists(sql_file_path):
        error_msg = f"SQL file {sql_file_path} does not exist, unable to import to the database."
        print(error_msg)
        return {"error": error_msg}

    conn, error = get_db_connection()
    if not conn:
        print(error)
        return {"error": error}

    cursor = None
    try:
        cursor = conn.cursor()

        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_commands = sql_file.read().split(';')
            for command in sql_commands:
                if command.strip():  # Ensure non-empty commands are executed
                    try:
                        cursor.execute(command)
                    except mysql.connector.Error as err:
                        print(f"Failed to execute SQL command: {err}\nCommand: {command.strip()}")
                        return {"error": f"SQL execution failed: {err}"}
                        
        conn.commit()
        print(f"SQL file {sql_file_path} successfully imported into the database")
        return {"message": "SQL import successful"}

    except mysql.connector.Error as err:
        print(f"Failed to import SQL file: {err}")
        return {"error": f"Failed to import SQL file: {err}"}

    except Exception as e:
        print(f"Error occurred during import process: {e}")
        return {"error": f"Error occurred during import process: {e}"}

    finally:
        if cursor:
            cursor.close()
        conn.close()

def main():
    """
    Main process for CSV conversion and SQL import.
    """
    conn, error = get_db_connection()
    if not conn:
        print(error)
        return

    if not os.path.exists(UPLOAD_FOLDER_CSV):
        print(f"Folder {UPLOAD_FOLDER_CSV} does not exist, please check the upload folder path.")
        return

    # Scan for all CSV files in /upload_csv folder
    csv_files = [f for f in os.listdir(UPLOAD_FOLDER_CSV) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found to process.")
        return

    for file_name in csv_files:
        file_path = os.path.join(UPLOAD_FOLDER_CSV, file_name)
        print(f"Processing file: {file_path}")
        try:
            sql_file_path = convert_csv_to_sql(file_path)
            import_result = import_sql_to_db(sql_file_path)
            print(import_result)
        except Exception as e:
            print(f"Error occurred while processing file {file_name}: {e}")

if __name__ == '__main__':
    main()
