import os
import sys

# Thêm đường dẫn thư mục gốc vào `sys.path`
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.database import Database

def fetch_latest_report():
    db = Database('postgresql://forecaster:1111@localhost:5432/finance_forecaster')
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT content FROM reports ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                with open("latest_report.md", "w", encoding="utf-8") as f:
                    f.write(row['content'])
                print("Lưu báo cáo vào file latest_report.md thành công!")
            else:
                print("Không tìm thấy báo cáo nào trong database.")

if __name__ == "__main__":
    fetch_latest_report()
