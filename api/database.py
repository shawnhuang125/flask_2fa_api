import mysql.connector
from api.config import Config

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        return None, f"資料庫連線失敗: {err}"

def insert_data(table, headers, data):
    conn, error = get_db_connection()
    if not conn:
        return {"error": error}

    cursor = conn.cursor()

    placeholders = ', '.join(['%s'] * len(headers))
    insert_query = f"INSERT INTO {table} ({', '.join(headers)}) VALUES ({placeholders})"

    try:
        cursor.executemany(insert_query, data)
        conn.commit()
        return {"message": f"數據已成功存入 {table}", "total_rows": len(data)}
    except Exception as e:
        conn.rollback()
        return {"error": f"數據存入失敗: {str(e)}"}
    finally:
        cursor.close()
        conn.close()
