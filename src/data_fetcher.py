import os
import pandas as pd
from datetime import datetime
# Import class Vnstock theo chuẩn repo
from vnstock import Vnstock

def fetch_bond_yields(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Lấy dữ liệu lịch sử lợi suất trái phiếu Chính phủ VN bằng thư viện Vnstock.
    Sử dụng biến môi trường VNSTOCK_API_KEY nếu có để mở rộng giới hạn.
    """
    print(f"Đang khởi tạo Vnstock client và lấy data từ {start_date} đến {end_date}...")
    
    # Lấy API Key từ biến môi trường
    api_key = os.getenv('VNSTOCK_API_KEY')
    
    try:
        # Khởi tạo Vnstock client. 
        # Theo mã nguồn vnstock, nếu có token, truyền trực tiếp vào constructor
        # Nếu không có, thư viện sẽ chạy ở chế độ công khai (Public API)
        if api_key:
            print("Đang sử dụng VNSTOCK_API_KEY để xác thực...")
            vs = Vnstock(token=api_key)
        else:
            print("Không tìm thấy API Key. Đang sử dụng Vnstock ở chế độ công khai...")
            vs = Vnstock()
            
        # Gọi module Bond. 
        # Sử dụng source='VCI' (Vietcap) - source này rất ổn định cho dữ liệu Macro/Bond
        # Anh/chị có thể thử source='TCBS' nếu muốn đổi nguồn dữ liệu.
        bond_data = vs.bond(source='VCI')
        
        # Gọi method lấy lịch sử lợi suất (Yield Curve History)
        # Tên method chính xác trong repo là `yield_historical` (hoặc `bond_yield` tùy version, lấy chuẩn mới nhất)
        df = bond_data.bond_yield(start_date=start_date, end_date=end_date)
        
        if df.empty:
            print("Cảnh báo: DataFrame trả về rỗng. Vui lòng kiểm tra lại khoảng thời gian hoặc source.")
            return pd.DataFrame()
            
        # 1. Chuẩn hóa cột thời gian
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        else:
            print("Cảnh báo: Không tìm thấy cột 'date' trong dữ liệu trả về.")
            return pd.DataFrame()
            
        # 2. Lọc các kỳ hạn chuẩn mực để phân tích Fixed Income
        # Vnstock thường trả về các kỳ hạn: 1W, 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 10Y, 15Y...
        standard_tenors = ['1Y', '5Y', '10Y']
        available_tenors = [t for t in standard_tenors if t in df.columns]
        
        if not available_tenors:
            print("Cảnh báo: Không tìm thấy các kỳ hạn chuẩn mực trong dữ liệu.")
            print("Các cột hiện có:", df.columns.tolist())
            return pd.DataFrame()
            
        df = df[available_tenors].copy()
        
        # 3. Đảm bảo dữ liệu dạng số (Numeric Coercion)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 4. Loại bỏ các dòng không có dữ liệu (NaN) và sắp xếp lại
        df = df.dropna()
        df = df.sort_index()
        
        print(f"Lấy dữ liệu thành công. Số dòng: {len(df)}")
        return df
        
    except Exception as e:
        # In ra lỗi cụ thể nếu API có sự thay đổi (Breaking change)
        print(f"Lỗi khi lấy dữ liệu qua Vnstock: {e}")
        return pd.DataFrame()
