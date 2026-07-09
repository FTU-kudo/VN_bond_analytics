import pandas as pd
from datetime import datetime, timedelta
from vnstock import bond

def fetch_bond_yields(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Lấy dữ liệu lợi suất trái phiếu chính phủ Việt Nam theo kỳ hạn.
    """
    print(f"Đang lấy dữ liệu từ {start_date} đến {end_date}...")
    try:
        # Sử dụng API của vnstock để lấy dữ liệu trái phiếu
        # Lưu ý: Tùy thuộc vào version vnstock, hàm có thể là bond_yield hoặc tương tự
        df = bond.bond_yield(start_date=start_date, end_date=end_date)
        
        # Giả sử dữ liệu trả về có cột 'date' và các cột kỳ hạn (1Y, 5Y, 10Y...)
        if df.empty:
            raise ValueError("Không có dữ liệu trả về từ API.")
            
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Chỉ giữ lại các kỳ hạn chuẩn mực cho Fixed Income Analysis
        standard_tenors = ['1Y', '5Y', '10Y']
        available_tenors = [t for t in standard_tenors if t in df.columns]
        df = df[available_tenors].dropna()
        
        print(f"Lấy dữ liệu thành công. Số dòng: {len(df)}")
        return df
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu: {e}")
        return pd.DataFrame()
