import os
import pandas as pd
from api.database import insert_data, get_db_connection

UPLOAD_FOLDER = "/upload_csv"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        headers = list(df.columns)
        data = df.values.tolist()

        conn, error = get_db_connection()
        if not conn:
            return {"error": error}, 500

        table_name = f"csv_table_{os.path.basename(file_path).split('.')[0]}"

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join([f'{col} TEXT' for col in headers])}
        )
        """

        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()

        response = insert_data(table_name, headers, data)
        return response, 200

    except Exception as e:
        return {"error": f"CSV 解析失敗: {str(e)}"}, 500
