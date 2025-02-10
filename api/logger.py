import logging
from logging.handlers import RotatingFileHandler
import os

# 定義日誌目錄和檔案
LOG_DIR = "logs"
LOG_FILE = "api.log"

# 如果日誌目錄不存在，則建立
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日誌全路徑
log_path = os.path.join(LOG_DIR, LOG_FILE)

# 定義日誌格式
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# 設定日誌轉動處理程式，每個日誌檔最大 1MB，最多保留 5 個備份
handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
handler.setFormatter(log_format)
handler.setLevel(logging.INFO)

# 建立全域日誌記錄器
logger = logging.getLogger("API_Logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 避免日誌重複記錄
logger.propagate = False
