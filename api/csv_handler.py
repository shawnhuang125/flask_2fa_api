import os
from api.database import convert_csv_to_sql, import_sql_to_db
import shutil

# 設定 CSV 和 SQL 檔案的儲存路徑
UPLOAD_FOLDER_CSV = os.path.join(os.getcwd(), 'upload_csv')
UPLOAD_FOLDER_SQL = os.path.join(os.getcwd(), 'upload_sql')
PROCESSED_FOLDER_CSV = os.path.join(os.getcwd(), 'processed_csv')  # 處理完成的 CSV 會移到這裡

# 確保 /upload_csv、/upload_sql 和 /processed_csv 資料夾存在
os.makedirs(UPLOAD_FOLDER_CSV, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SQL, exist_ok=True)
os.makedirs(PROCESSED_FOLDER_CSV, exist_ok=True)

def process_csv(file_path):
    
    # 處理 CSV 檔案：將其轉換為 SQL 並匯入資料庫。
    
    try:
        print(f"開始轉換 CSV 檔案: {file_path}")
        
        # 轉換 CSV 檔案為 SQL 語法檔案，儲存到 /upload_sql 資料夾
        sql_file_path = convert_csv_to_sql(file_path, UPLOAD_FOLDER_SQL)
        print(f"SQL 檔案已成功儲存至 {sql_file_path}")

        # 將生成的 SQL 檔案匯入資料庫
        import_result = import_sql_to_db(sql_file_path)
        if 'error' in import_result:
            print(f"匯入資料庫失敗: {import_result['error']}")
            return {"error": import_result['error']}, 500

        print(f"CSV 檔案已成功匯入資料庫: {file_path}")
        return {"message": "CSV 檔案已成功匯入資料庫"}, 200

    except Exception as e:
        print(f"CSV 解析失敗: {e}")
        return {"error": f"CSV 解析失敗: {str(e)}"}, 500

def move_processed_file(file_path):
    
    # 將已處理的 CSV 檔案移動到 /processed_csv 資料夾。
    
    try:
        filename = os.path.basename(file_path)
        destination = os.path.join(PROCESSED_FOLDER_CSV, filename)
        shutil.move(file_path, destination)
        print(f"已將處理完成的檔案移動至 {destination}")
    except Exception as e:
        print(f"無法移動檔案 {file_path}: {e}")

if __name__ == '__main__':
    # 遍歷 /upload_csv 資料夾中的所有 CSV 檔案
    csv_files = [f for f in os.listdir(UPLOAD_FOLDER_CSV) if f.endswith('.csv')]

    if not csv_files:
        print("沒有找到 CSV 檔案需要處理。")
    
    for file_name in csv_files:
        file_path = os.path.join(UPLOAD_FOLDER_CSV, file_name)
        print(f"開始處理檔案: {file_path}")
        
        response, status_code = process_csv(file_path)
        print(response)

        # 如果處理成功，將 CSV 檔案移動到 processed_csv 資料夾
        if status_code == 200:
            move_processed_file(file_path)
