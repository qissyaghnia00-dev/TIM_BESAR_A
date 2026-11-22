import pandas as pd

def split_time_series_data(file_path, date_column='tanggal_transaksi', test_ratio=0.2):
    """
    Memisahkan dataset transaksi berdasarkan urutan waktu (Time-Based Split).
    80% data terlama -> diserahkan ke Tim Model (data_latih.csv)
    20% data terbaru -> diserahkan HANYA ke Tim Penguji (data_uji_holdout.csv)
    """
    print("Memuat dataset...")
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Format file harus .csv atau .xlsx")

    # 1. Pastikan format tanggal seragam dan urutkan dari terlama ke terbaru
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(by=date_column).reset_index(drop=True)

    # 2. Tentukan batas tanggal pemisahan (tidak boleh diacak!)
    unique_dates = df[date_column].unique()
    split_index = int(len(unique_dates) * (1 - test_ratio))
    split_date = unique_dates[split_index]

    # 3. Pisahkan data berdasarkan tanggal batas tersebut
    train_data = df[df[date_column] < split_date]
    test_data = df[df[date_column] >= split_date]

    # 4. Simpan ke dua file terpisah
    train_data.to_csv("data_latih_tim_model.csv", index=False)
    test_data.to_csv("data_uji_holdout_tim_penguji.csv", index=False)

    print("\n=== PEMISAHAN DATA SELESAI (TIME-BASED SPLIT) ===")
    print(f"Total Hari Unik      : {len(unique_dates)} hari")
    print(f"Batas Tanggal Split  : {pd.to_datetime(split_date).strftime('%Y-%m-%d')}")
    print(f"1. Data Latih        : {len(train_data)} baris -> Simpan ke 'data_latih_tim_model.csv' (Untuk Tim Model)")
    print(f"2. Data Uji Hold-Out : {len(test_data)} baris -> Simpan ke 'data_uji_holdout_tim_penguji.csv' (KHUSUS Tim Penguji)")

# --- CARA PENGGUNAAN ---
if __name__ == "__main__":
    # Ganti 'data_bersih_umkm.xlsx' dengan nama file asli dari mitra Anda
    nama_file_mitra = "data_bersih_umkm.xlsx" 
    
    try:
        split_time_series_data(nama_file_mitra, date_column='tanggal_transaksi', test_ratio=0.2)
    except FileNotFoundError:
        print(f"File '{nama_file_mitra}' belum ditemukan. Pastikan nama file sesuai dengan yang ada di folder Anda.")
