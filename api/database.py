import mysql.connector
from api.config import Config
import os
import datetime
import pandas as pd

# 設定上傳及儲存資料夾
UPLOAD_FOLDER_CSV = os.path.join(os.getcwd(), 'upload_csv')
UPLOAD_FOLDER_SQL = os.path.join(os.getcwd(), 'upload_sql')

# 確保 /upload_csv 和 /upload_sql 資料夾存在
os.makedirs(UPLOAD_FOLDER_CSV, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SQL, exist_ok=True)

def get_db_connection():
    """
    建立資料庫連線，並返回連線物件或錯誤訊息。
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        print("成功連接到資料庫")
        return conn, None
    except mysql.connector.Error as err:
        print(f"資料庫連線失敗: {err}")
        return None, f"資料庫連線失敗: {err}"

def convert_csv_to_sql(file_path, output_folder=UPLOAD_FOLDER_SQL):
    """
    將 CSV 檔案轉換為 SQL 語法檔案，並儲存到指定的資料夾。
    """
    try:
        df = pd.read_csv(file_path)

        # 驗證 CSV 檔案是否包含必要欄位
        expected_columns = ['name', 'address', 'phone', 'rating', 'opening_hours', 'review_author', 'review_rating', 'review_text']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV 檔案缺少必要欄位: {', '.join(missing_columns)}")
        
        # 以當前時間戳命名資料表和 SQL 檔案（避免不一致）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = f"places_reviews_{timestamp}"

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

        # 處理 SQL 字串中的特殊字元
        def escape_sql_string(value):
            if pd.isnull(value):
                return None
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

            # 格式化插入語句，處理 NULL 值
            formatted_values = [f"'{v}'" if v is not None else 'NULL' for v in values]
            insert_query = f"""
            INSERT INTO `{table_name}` 
            (name, address, phone, rating, opening_hours, review_author, review_rating, review_text) 
            VALUES ({', '.join(formatted_values)});
            """
            insert_statements.append(insert_query)

        # 儲存 SQL 檔案到指定資料夾
        sql_file_name = f"{table_name}.sql"
        sql_file_path = os.path.join(output_folder, sql_file_name)
        with open(sql_file_path, "w", encoding="utf-8") as sql_file:
            sql_file.write(create_table_sql + "\n")
            sql_file.write("\n".join(insert_statements))

        print(f"SQL 檔案已成功儲存至 {sql_file_path}")
        return sql_file_path

    except Exception as e:
        print(f"CSV 轉換失敗: {e}")
        raise

def import_sql_to_db(sql_file_path):
    """
    將 SQL 檔案匯入資料庫。
    """
    if not os.path.exists(sql_file_path):
        error_msg = f"SQL 檔案 {sql_file_path} 不存在，無法匯入資料庫。"
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
                if command.strip():  # 確保不執行空語句
                    try:
                        cursor.execute(command)
                    except mysql.connector.Error as err:
                        print(f"執行 SQL 指令失敗: {err}\n指令: {command.strip()}")
                        return {"error": f"SQL 執行失敗: {err}"}
                        
        conn.commit()
        print(f"SQL 檔案 {sql_file_path} 已成功匯入資料庫")
        return {"message": "SQL 匯入成功"}

    except mysql.connector.Error as err:
        print(f"匯入 SQL 檔案失敗: {err}")
        return {"error": f"匯入 SQL 檔案失敗: {err}"}

    except Exception as e:
        print(f"匯入過程中發生錯誤: {e}")
        return {"error": f"匯入過程中發生錯誤: {e}"}

    finally:
        if cursor:
            cursor.close()
        conn.close()

def main():
    """
    執行 CSV 轉換與匯入的主流程。
    """
    conn, error = get_db_connection()
    if not conn:
        print(error)
        return

    if not os.path.exists(UPLOAD_FOLDER_CSV):
        print(f"資料夾 {UPLOAD_FOLDER_CSV} 不存在，請確認上傳資料夾路徑。")
        return

    # 遍歷 /upload_csv 資料夾中的所有 CSV 檔案
    csv_files = [f for f in os.listdir(UPLOAD_FOLDER_CSV) if f.endswith('.csv')]

    if not csv_files:
        print("沒有找到 CSV 檔案需要處理。")
        return

    for file_name in csv_files:
        file_path = os.path.join(UPLOAD_FOLDER_CSV, file_name)
        print(f"正在處理檔案: {file_path}")
        try:
            sql_file_path = convert_csv_to_sql(file_path)
            import_result = import_sql_to_db(sql_file_path)
            print(import_result)
        except Exception as e:
            print(f"處理檔案 {file_name} 時發生錯誤: {e}")

if __name__ == '__main__':
    main()
