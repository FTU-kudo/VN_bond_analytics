import os
import pandas as pd
from datetime import datetime
from data_fetcher import fetch_bond_yields
from report_generator import generate_html_dashboard, generate_pdf_report

def main():
    # Khởi tạo thư mục output nếu chưa có
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Định nghĩa khoảng thời gian (2016 - 2026)
    start_date = '2016-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

    # 1. Lấy dữ liệu
    df = fetch_bond_yields(start_date, end_date)
    
    if df.empty:
        print("Pipeline dừng lại do không có dữ liệu.")
        return

    # 2. Xuất file CSV (Historical Data)
    csv_path = os.path.join(output_dir, 'bond_data.csv')
    df.to_csv(csv_path)
    print(f"Đã xuất file CSV: {csv_path}")

    # 3. Xuất file HTML
    html_path = os.path.join(output_dir, 'bond_dashboard.html')
    generate_html_dashboard(df, html_path)

    # 4. Xuất file PDF
    pdf_path = os.path.join(output_dir, 'bond_report.pdf')
    generate_pdf_report(df, pdf_path)

if __name__ == "__main__":
    main()
