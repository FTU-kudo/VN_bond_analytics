import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF, XPos, YPos


def generate_html_dashboard(df: pd.DataFrame, output_path: str):
    """Tạo file HTML trực quan hóa bằng Plotly cao cấp (Light Executive White Theme)."""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    all_tenors = [col for col in ['3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y'] if col in df.columns]
    core_tenors = [col for col in ['3Y', '5Y', '7Y', '10Y', '15Y'] if col in df.columns]

    # Tính toán các chỉ số KPI
    latest_row = df.iloc[-1]
    step_1yr = 260 if len(df) > 1000 else 52
    step_5yr = 1300 if len(df) > 1000 else 260
    prev_year_idx = max(0, len(df) - step_1yr)
    prev_year_row = df.iloc[prev_year_idx]

    current_10y = latest_row.get('10Y', 0)
    prev_10y = prev_year_row.get('10Y', 0)
    diff_10y = current_10y - prev_10y

    spread_10y_1y = latest_row.get('Spread_10Y_1Y', current_10y - latest_row.get('1Y', 0))
    curve_slope = latest_row.get('Curve_Slope', 'Bình thường')
    avg_10y = df['10Y'].mean() if '10Y' in df.columns else 0
    min_10y = df['10Y'].min() if '10Y' in df.columns else 0
    max_10y = df['10Y'].max() if '10Y' in df.columns else 0

    # 1. Biểu đồ lịch sử lợi suất (Tập trung vào 5 kỳ hạn chủ đạo 3Y-15Y chiếm >80% khối lượng)
    fig1 = go.Figure()
    colors = {
        '3Y': '#2563eb',   # Deep Royal Blue
        '5Y': '#7c3aed',   # Vibrant Purple
        '7Y': '#db2777',   # Deep Magenta
        '10Y': '#059669',  # Emerald Green (Bold benchmark)
        '15Y': '#d97706'   # Warm Amber
    }
    for col in core_tenors:
        fig1.add_trace(go.Scatter(
            x=df.index, y=df[col],
            mode='lines', name=f'Kỳ hạn {col}',
            line=dict(width=3.0 if col == '10Y' else 1.8, color=colors.get(col, '#475569'))
        ))
    fig1.update_layout(
        title='Lịch sử Lợi suất Trái phiếu Chính phủ Việt Nam - Các kỳ hạn chủ đạo (3Y - 15Y)',
        xaxis_title='Thời gian', yaxis_title='Lợi suất (%)',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#ffffff',
        font=dict(family='Inter, sans-serif', size=13, color='#0f172a'),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='white', bordercolor='#cbd5e1', font=dict(family='Inter, sans-serif', size=13, color='#0f172a')),
        legend=dict(font=dict(color='#0f172a', size=12), bgcolor='rgba(255,255,255,0.9)', bordercolor='#e2e8f0', borderwidth=1),
        height=430,
        margin=dict(l=45, r=40, t=60, b=40)
    )
    fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')

    # 2. Biểu đồ cấu trúc đường cong lợi suất (Toàn bộ 11 kỳ hạn)
    fig2 = go.Figure()
    idx_1yr_ago = max(0, len(df) - step_1yr)
    idx_5yr_ago = max(0, len(df) - step_5yr)

    fig2.add_trace(go.Scatter(
        x=all_tenors, y=[latest_row[t] for t in all_tenors],
        mode='lines+markers', name=f'Hiện tại ({df.index[-1].strftime("%d/%m/%Y")})',
        line=dict(color='#059669', width=3), marker=dict(size=8)
    ))
    fig2.add_trace(go.Scatter(
        x=all_tenors, y=[df.iloc[idx_1yr_ago][t] for t in all_tenors],
        mode='lines+markers', name=f'1 năm trước ({df.index[idx_1yr_ago].strftime("%d/%m/%Y")})',
        line=dict(color='#2563eb', width=2, dash='dash'), marker=dict(size=6)
    ))
    fig2.add_trace(go.Scatter(
        x=all_tenors, y=[df.iloc[idx_5yr_ago][t] for t in all_tenors],
        mode='lines+markers', name=f'5 năm trước ({df.index[idx_5yr_ago].strftime("%d/%m/%Y")})',
        line=dict(color='#d97706', width=2, dash='dot'), marker=dict(size=6)
    ))
    fig2.update_layout(
        title='Cấu trúc Đường cong Lợi suất (Yield Curve Term Structure - 11 Kỳ hạn)',
        xaxis_title='Kỳ hạn', yaxis_title='Lợi suất (%)',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#ffffff',
        font=dict(family='Inter, sans-serif', size=13, color='#0f172a'),
        hoverlabel=dict(bgcolor='white', bordercolor='#cbd5e1', font=dict(family='Inter, sans-serif', size=13, color='#0f172a')),
        legend=dict(font=dict(color='#0f172a', size=12), bgcolor='rgba(255,255,255,0.9)', bordercolor='#e2e8f0', borderwidth=1),
        height=380,
        margin=dict(l=45, r=40, t=60, b=40)
    )
    fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')

    # 3. Biểu đồ chênh lệch 10Y - 1Y
    fig3 = go.Figure()
    if 'Spread_10Y_1Y' in df.columns:
        fig3.add_trace(go.Scatter(
            x=df.index, y=df['Spread_10Y_1Y'],
            mode='lines', name='Spread 10Y - 1Y',
            fill='tozeroy', fillcolor='rgba(5, 150, 105, 0.12)',
            line=dict(color='#059669', width=2)
        ))
    fig3.update_layout(
        title='Chênh lệch Lợi suất Kỳ hạn 10Y - 1Y (Term Spread %)',
        xaxis_title='Thời gian', yaxis_title='Spread (%)',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#ffffff',
        font=dict(family='Inter, sans-serif', size=13, color='#0f172a'),
        hoverlabel=dict(bgcolor='white', bordercolor='#cbd5e1', font=dict(family='Inter, sans-serif', size=13, color='#0f172a')),
        height=380,
        margin=dict(l=45, r=40, t=60, b=40)
    )
    fig3.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    fig3.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')

    # Render sang chuỗi HTML
    plot1_html = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    plot2_html = fig2.to_html(full_html=False, include_plotlyjs=False)
    plot3_html = fig3.to_html(full_html=False, include_plotlyjs=False)

    # Bảng dữ liệu HTML (20 quan sát ngày gần nhất cho các kỳ hạn chính)
    recent_df = df.tail(20).iloc[::-1]
    table_rows = []
    for dt, row in recent_df.iterrows():
        tds = [f"<td><strong>{dt.strftime('%d/%m/%Y')}</strong></td>"]
        for t in core_tenors:
            tds.append(f"<td>{row.get(t, '-'):.3f}%</td>")
        sp = row.get('Spread_10Y_1Y', '-')
        tds.append(f"<td>{sp:.3f}%</td>" if isinstance(sp, (int, float)) else "<td>-</td>")
        table_rows.append(f"<tr>{''.join(tds)}</tr>")

    th_cols = "".join([f"<th>Kỳ hạn {t}</th>" for t in core_tenors])

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phân tích Lợi suất Trái phiếu Chính phủ Việt Nam (2016-2026)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{
            background-color: #f8fafc;
            color: #0f172a;
            min-height: 100vh;
            padding: 32px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 32px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
            margin-bottom: 28px;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
        }}
        .header .subtitle {{ font-size: 14px; color: #64748b; margin-top: 4px; }}
        .badge {{
            padding: 8px 16px;
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            color: #059669;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }}
        .kpi-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-3px);
            border-color: #cbd5e1;
        }}
        .kpi-title {{ font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: #0f172a; margin: 10px 0 6px 0; }}
        .kpi-desc {{ font-size: 13px; color: #059669; font-weight: 500; }}
        .chart-container {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 28px;
        }}
        @media (max-width: 1024px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
        .table-container {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
            overflow-x: auto;
        }}
        .table-container h2 {{ font-size: 18px; margin-bottom: 16px; color: #0f172a; font-weight: 700; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th, td {{
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid #f1f5f9;
        }}
        th {{
            background: #f8fafc;
            color: #475569;
            font-weight: 600;
        }}
        tr:hover {{ background: #f8fafc; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Hệ Thống Phân Tích Lợi Suất Trái Phiếu Chính Phủ Việt Nam</h1>
            <div class="subtitle">Tập trung kỳ hạn chủ đạo KBNN & Thứ cấp (3Y - 15Y) | Dữ liệu chính thức từ Sở GDCK Hà Nội (HNX)</div>
        </div>
        <div class="badge">Cập nhật: {df.index[-1].strftime('%d/%m/%Y')}</div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Lợi suất 10Y Hiện Tại</div>
            <div class="kpi-value">{current_10y:.2f}%</div>
            <div class="kpi-desc">Thay đổi YoY: {diff_10y:+.2f}%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Term Spread (10Y - 1Y)</div>
            <div class="kpi-value">{spread_10y_1y:.2f}%</div>
            <div class="kpi-desc">Trạng thái: {curve_slope}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Lợi suất 10Y Trung Bình (10 Năm)</div>
            <div class="kpi-value">{avg_10y:.2f}%</div>
            <div class="kpi-desc">Biên độ 10 năm: {min_10y:.2f}% - {max_10y:.2f}%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Tổng Số Quan Sát</div>
            <div class="kpi-value">{len(df)}</div>
            <div class="kpi-desc">Từ {df.index[0].strftime('%Y')} đến {df.index[-1].strftime('%Y')} (Theo ngày)</div>
        </div>
    </div>

    <div class="chart-container">
        {plot1_html}
    </div>

    <div class="grid-2">
        <div class="chart-container" style="margin-bottom:0;">
            {plot2_html}
        </div>
        <div class="chart-container" style="margin-bottom:0;">
            {plot3_html}
        </div>
    </div>

    <div class="table-container">
        <h2>Bảng Dữ Liệu Lợi Suất TPCP Lịch Sử (20 Ngày Gần Nhất - Các Kỳ Hạn Chủ Đạo)</h2>
        <table>
            <thead>
                <tr>
                    <th>Ngày</th>
                    {th_cols}
                    <th>Spread 10Y-1Y</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[+] Đã tạo file HTML Dashboard trực quan: {output_path}")


def generate_pdf_report(df: pd.DataFrame, output_path: str):
    """Tạo file PDF báo cáo phân tích định lượng chuyên sâu (hỗ trợ Tiếng Việt Unicode chuẩn)."""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    # 1. Tạo hình ảnh biểu đồ bằng Matplotlib/Seaborn để nhúng vào PDF
    sns.set_theme(style="whitegrid")
    img_path1 = 'output/temp_chart1.png'
    img_path2 = 'output/temp_chart2.png'

    # Figure 1: Lịch sử lợi suất các kỳ hạn chính (1Y, 3Y, 5Y, 10Y)
    plt.figure(figsize=(10, 4.2), dpi=300)
    for col in ['1Y', '3Y', '5Y', '10Y']:
        if col in df.columns:
            plt.plot(df.index, df[col], label=f'Kỳ hạn {col}', linewidth=2 if col == '10Y' else 1.2)
    plt.title('LICH SU LOI SUAT TRAI PHIEU CHINH PHU VIET NAM (2016 - 2026)', fontsize=12, fontweight='bold')
    plt.ylabel('Loi suat (%)', fontsize=10)
    plt.xlabel('Thoi gian', fontsize=10)
    plt.legend(frameon=True, loc='upper right')
    plt.tight_layout()
    plt.savefig(img_path1)
    plt.close()

    # Figure 2: Cấu trúc đường cong lợi suất
    tenors = [col for col in ['3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y'] if col in df.columns]
    latest_row = df.iloc[-1]
    step_1yr = 260 if len(df) > 1000 else 52
    idx_1yr_ago = max(0, len(df) - step_1yr)

    plt.figure(figsize=(10, 3.8), dpi=300)
    plt.plot(tenors, [latest_row[t] for t in tenors], marker='o', linewidth=2.5, color='#059669', label=f'Hien tai ({df.index[-1].strftime("%d/%m/%Y")})')
    plt.plot(tenors, [df.iloc[idx_1yr_ago][t] for t in tenors], marker='s', linestyle='--', color='#2563eb', label=f'1 nam truoc ({df.index[idx_1yr_ago].strftime("%d/%m/%Y")})')
    plt.title('CAU TRUC DUONG CONG LOI SUAT (YIELD CURVE TERM STRUCTURE)', fontsize=12, fontweight='bold')
    plt.ylabel('Loi suat (%)', fontsize=10)
    plt.xlabel('Ky han', fontsize=10)
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(img_path2)
    plt.close()

    # 2. Khởi tạo FPDF với font Unicode Việt Nam (Arial)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_regular = 'src/fonts/arial.ttf'
    font_bold = 'src/fonts/arialbd.ttf'

    has_vn_font = os.path.exists(font_regular) and os.path.exists(font_bold)
    if has_vn_font:
        pdf.add_font("ArialVN", style="", fname=font_regular)
        pdf.add_font("ArialVN", style="B", fname=font_bold)
        family = "ArialVN"
    else:
        family = "Helvetica"

    # Header
    pdf.set_font(family, "B", 17)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "BÁO CÁO PHÂN TÍCH LỢI SUẤT TRÁI PHIẾU CHÍNH PHỦ VIỆT NAM", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font(family, "", 11)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 7, f"Giai đoạn phân tích: 10 năm (2016 - 2026) | Cập nhật ngày: {df.index[-1].strftime('%d/%m/%Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)

    # Khái quát thị trường
    pdf.set_font(family, "B", 13)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "1. Tóm Tắt Điểm Nhấn Định Lượng Thị Trường Trái Phiếu", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font(family, "", 10.5)
    pdf.set_text_color(51, 65, 85)

    current_10y = latest_row.get('10Y', 0)
    current_1y = latest_row.get('1Y', 0)
    spread = current_10y - current_1y
    slope = latest_row.get('Curve_Slope', 'Bình thường')

    summary_text = (
        f"- Lợi suất Trái phiếu Chính phủ kỳ hạn 10 năm hiện đạt {current_10y:.2f}%, "
        f"trong khi kỳ hạn 1 năm đạt {current_1y:.2f}%.\n"
        f"- Chênh lệch kỳ hạn dài - ngắn (Spread 10Y - 1Y) ở mức {spread:+.2f}%, "
        f"thể hiện cấu trúc đường cong lợi suất '{slope}'.\n"
        f"- So sánh lịch sử 10 năm (2016 - 2026), mặt bằng lợi suất hiện tại phản ánh chính sách "
        f"tiền tệ ổn định và thanh khoản hệ thống ngân hàng duy trì trạng thái dồi dào."
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(4)

    # Nhúng Biểu đồ 1
    if os.path.exists(img_path1):
        pdf.image(img_path1, x=15, w=180)
        pdf.ln(3)

    # Trang 2: Bảng số liệu & Khuyến nghị
    pdf.add_page()
    pdf.set_font(family, "B", 13)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "2. Thống Kê Mô Tả Lợi Suất Các Kỳ Hạn Chuẩn (2016 - 2026)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # Table Header
    pdf.set_font(family, "B", 10)
    pdf.set_fill_color(241, 245, 249)
    cols = ["Kỳ hạn", "Hiện tại", "Trung bình", "Đáy (Min)", "Đỉnh (Max)", "Độ lệch chuẩn"]
    widths = [28, 30, 32, 32, 32, 34]
    for i, h in enumerate(cols):
        pdf.cell(widths[i], 8, h, border=1, align="C", fill=True)
    pdf.ln()

    # Table Rows
    pdf.set_font(family, "", 9.5)
    for t in tenors:
        s = df[t].dropna()
        row_vals = [
            f"G-Bond {t}",
            f"{latest_row[t]:.2f}%",
            f"{s.mean():.2f}%",
            f"{s.min():.2f}%",
            f"{s.max():.2f}%",
            f"{s.std():.2f}%"
        ]
        for i, val in enumerate(row_vals):
            pdf.cell(widths[i], 7.5, val, border=1, align="C")
        pdf.ln()

    pdf.ln(6)

    # Nhúng Biểu đồ 2
    if os.path.exists(img_path2):
        pdf.image(img_path2, x=15, w=180)
        pdf.ln(3)

    # Khuyến nghị danh mục
    pdf.set_font(family, "B", 13)
    pdf.cell(0, 8, "3. Khuyến Nghị Chiến Lược Đầu Tư Fixed Income", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(family, "", 10)
    reco_text = (
        "- Chiến lược Thời lượng (Duration Strategy): Với đường cong lợi suất dốc lên chuẩn mực, "
        "nhà đầu tư danh mục TPCP có thể tận dụng mức chênh lệch kỳ hạn (roll-down return) ở vùng kỳ hạn 3Y - 7Y.\n"
        "- Quản trị rủi ro: Cần theo dõi chặt chẽ áp lực tỷ giá và lạm phát toàn cầu để kịp thời tái cơ cấu "
        "thời lượng danh mục trong trường hợp Ngân hàng Nhà nước điều chỉnh chính sách tiền tệ."
    )
    pdf.multi_cell(0, 6, reco_text)

    pdf.output(output_path)
    print(f"[+] Đã tạo file PDF Báo cáo chuyên sâu chuẩn Tiếng Việt: {output_path}")

    for temp_img in [img_path1, img_path2]:
        if os.path.exists(temp_img):
            os.remove(temp_img)

