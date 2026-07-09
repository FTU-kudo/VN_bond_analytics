import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def generate_html_dashboard(df: pd.DataFrame, output_path: str):
    """Tạo file HTML trực quan hóa bằng Plotly"""
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=f'G-Bond {col}'))
    
    fig.update_layout(
        title='Biểu đồ Lịch sử Lợi suất Trái phiếu Chính phủ VN (2016 - 2026)',
        xaxis_title='Ngày',
        yaxis_title='Lợi suất (%)',
        template='plotly_dark',
        hovermode='x unified'
    )
    fig.write_html(output_path)
    print(f"Đã xuất file HTML: {output_path}")

def generate_pdf_report(df: pd.DataFrame, output_path: str):
    """Tạo file PDF báo cáo phân tích"""
    plt.figure(figsize=(10, 4))
    for col in df.columns:
        plt.plot(df.index, df[col], label=f'G-Bond {col}')
    plt.title('Lịch sử Lợi suất Trái phiếu VN')
    plt.ylabel('Lợi suất (%)')
    plt.legend()
    plt.grid(True)
    img_path = 'output/temp_chart.png'
    plt.savefig(img_path)
    plt.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, "Bao cao Phan tich Lai suat Trai phieu VN", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=10)
    pdf.cell(200, 10, f"Khoang thoi gian: {df.index.min().date()} den {df.index.max().date()}", ln=True)
    
    # Thống kê cơ bản (Yield Spread Analysis)
    if '10Y' in df.columns and '1Y' in df.columns:
        spread = df['10Y'] - df['1Y']
        pdf.cell(200, 10, f"Spread 10Y-1Y trung binh: {spread.mean():.2f}% | Hien tai: {spread.iloc[-1]:.2f}%", ln=True)
        if spread.iloc[-1] < 0:
            pdf.cell(200, 10, "Canh bao: Duong cong loi suat nguoc (Inverted Yield Curve)", ln=True)

    pdf.ln(10)
    pdf.image(img_path, w=180)
    pdf.output(output_path)
    
    if os.path.exists(img_path):
        os.remove(img_path)
    print(f"Đã xuất file PDF: {output_path}")
