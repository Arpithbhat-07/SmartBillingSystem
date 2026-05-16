import shutil
import os
from datetime import datetime

BASE_PATH = os.path.expanduser("~/OneDrive/ServiceCenterSystem")
DB_PATH = os.path.join(BASE_PATH, "database", "billing.db")
BACKUP_PATH = os.path.join(BASE_PATH, "backups")

def backup_database():
    os.makedirs(BACKUP_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_file = os.path.join(BACKUP_PATH, f"billing_{timestamp}.db")
    shutil.copy(DB_PATH, backup_file)