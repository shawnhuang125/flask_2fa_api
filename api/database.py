import mysql.connector
from api.config import Config
import os
import datetime
import pandas as pd
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn, None
    except mysql.connector.Error as err:
        return None, f"資料庫連線失敗: {err}"

def convert_csv_to_sql(file_path):
    df = pd.read_csv(file_path)
    
    table_name = "places_reviews"
    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
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

    def escape_sql_string(value):
        if isinstance(value, str):
            return value.replace("'", "''")
        return value

    insert_statements = []
    for _, row in df.iterrows():
        values = (
            escape_sql_string(row['name']),
            escape_sql_string(row['address']),
            escape_sql_string(row['phone']),
            row['rating'],
            escape_sql_string(row['opening_hours']),
            escape_sql_string(row['review_author']),
            row['review_rating'],
            escape_sql_string(row['review_text'])
        )
        insert_query = f"INSERT INTO {table_name} (name, address, phone, rating, opening_hours, review_author, review_rating, review_text) VALUES ('{values[0]}', '{values[1]}', '{values[2]}', {values[3]}, '{values[4]}', '{values[5]}', {values[6]}, '{values[7]}');"
        insert_statements.append(insert_query)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_sql_path = f"places_reviews_{timestamp}.sql"
    with open(output_sql_path, "w", encoding="utf-8") as sql_file:
        sql_file.write(create_table_sql + "\n")
        sql_file.write("\n".join(insert_statements))

    print(f"SQL 檔案已成功儲存至 {output_sql_path}")
    return output_sql_path

def import_sql_to_db(sql_file_path):
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()

        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_commands = sql_file.read().split(';')
            for command in sql_commands:
                if command.strip():  # 確保不執行空語句
                    cursor.execute(command)
        conn.commit()
        print(f"SQL 檔案 {sql_file_path} 已成功匯入資料庫")
    except mysql.connector.Error as err:
        print(f"匯入 SQL 檔案失敗: {err}")
    finally:
        cursor.close()
        conn.close()

# 執行轉換與匯入
def main():
    conn, error = get_db_connection()
    if conn:
        upload_dir = "upload_csv"
        for file_name in os.listdir(upload_dir):
            if file_name.endswith(".csv"):
                file_path = os.path.join(upload_dir, file_name)
                sql_file_path = convert_csv_to_sql(file_path)
                import_sql_to_db(sql_file_path)

if __name__ == '__main__':
    main()
