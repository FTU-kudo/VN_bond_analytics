import os
import sys
import pandas as pd
from datetime import datetime
from data_fetcher import fetch_bond_yields
from report_generator import generate_html_dashboard, generate_pdf_report


def main():
    # Cấu hình UTF-8 cho console output
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("==================================================================")
    print(" HỆ THỐNG PHÂN TÍCH LỢI SUẤT TRÁI PHIẾU CHÍNH PHỦ VIỆT NAM")
    print(" Khung thời gian: 10 Năm (2016 - 2026) | Tự động hóa hàng tuần")
    print("==================================================================\n")

    # Khởi tạo thư mục output
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    start_date = '2016-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

    # 1. Thu thập và tổng hợp dữ liệu lợi suất Trái phiếu Chính phủ Việt Nam
    df = fetch_bond_yields(start_date, end_date)
    if df.empty:
        print("[!] Lỗi: Pipeline dừng lại do không thu thập được dữ liệu.")
        return

    # 2. Xuất file 1: Dữ liệu lịch sử (Excel XLSX 2 Sheet & CSV)
    xlsx_path = os.path.join(output_dir, 'bond_data.xlsx')
    csv_core_path = os.path.join(output_dir, 'bond_data.csv')
    csv_full_path = os.path.join(output_dir, 'bond_data_full_11_tenors.csv')

    # Chuẩn bị Sheet 1 (Chuẩn chủ đạo 3Y - 5Y - 7Y - 10Y - 15Y)
    core_cols = [c for c in ['3Y', '5Y', '7Y', '10Y', '15Y', 'Spread_10Y_1Y', 'Spread_10Y_2Y', 'Curve_Slope'] if c in df.columns]
    df_sheet1 = df[core_cols].copy()

    # Sheet 2 (Toàn bộ 11 kỳ hạn từ 3M đến 20Y)
    df_sheet2 = df.copy()

    try:
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            df_sheet1.to_excel(writer, sheet_name='Ky_han_chinh_3Y_15Y')
            df_sheet2.to_excel(writer, sheet_name='Toan_bo_11_ky_han')
        df_sheet1.to_csv(csv_core_path, encoding='utf-8-sig')
        df_sheet2.to_csv(csv_full_path, encoding='utf-8-sig')
        print(f"[1/3] Đã xuất file Excel 2 Sheet: {xlsx_path}")
        print(f"      - Sheet 1 (3Y-15Y) CSV: {csv_core_path}")
        print(f"      - Sheet 2 (3M-20Y) CSV: {csv_full_path}")
    except PermissionError:
        fallback_xlsx = os.path.join(output_dir, 'bond_data_latest.xlsx')
        with pd.ExcelWriter(fallback_xlsx, engine='openpyxl') as writer:
            df_sheet1.to_excel(writer, sheet_name='Ky_han_chinh_3Y_15Y')
            df_sheet2.to_excel(writer, sheet_name='Toan_bo_11_ky_han')
        print(f"[1/3] Cảnh báo file đang mở. Đã lưu Excel 2 sheet vào: {fallback_xlsx}")

    # 3. Xuất file 2: Dashboard trực quan HTML (Interactive Dashboard)
    html_path = os.path.join(output_dir, 'bond_dashboard.html')
    try:
        generate_html_dashboard(df, html_path)
        print(f"[2/3] Đã xuất file Dashboard trực quan HTML: {html_path}")
    except PermissionError:
        fallback_html = os.path.join(output_dir, 'bond_dashboard_latest.html')
        generate_html_dashboard(df, fallback_html)
        print(f"[2/3] Đã lưu Dashboard HTML vào: {fallback_html}")

    # 4. Xuất file 3: Báo cáo định lượng PDF (Institutional PDF Report)
    pdf_path = os.path.join(output_dir, 'bond_report.pdf')
    try:
        generate_pdf_report(df, pdf_path)
        print(f"[3/3] Đã xuất file Báo cáo phân tích PDF: {pdf_path}")
    except PermissionError:
        fallback_pdf = os.path.join(output_dir, 'bond_report_latest.pdf')
        generate_pdf_report(df, fallback_pdf)
        print(f"[3/3] Đã lưu Báo cáo PDF vào: {fallback_pdf}")

    print("\n==================================================================")
    print(" Hoàn tất toàn bộ quy trình Phân tích & Tạo Báo cáo Trái phiếu VN")
    print(" 3 file kết quả đã sẵn sàng trong thư mục output/")
    print("==================================================================")


if __name__ == "__main__":
    main()

