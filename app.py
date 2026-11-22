import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Asisten Restock & Ramalan UMKM", page_icon="📦", layout="wide")

st.title("📦 Peramal Penjualan & Rekomendasi Restock UMKM")
st.markdown("Unggah data riwayat transaksi harian (minimal 6 bulan) untuk memprediksi permintaan dan menghitung saran kulakan.")

# --- FUNGSI DATA DUMMY (SIMULASI) ---
@st.cache_data
def generate_dummy_data():
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=180)
    data = []
    products = {
        "Kopi Susu Gula Aren": (45, 12),
        "Roti Bakar Cokelat": (30, 8),
        "Es Teh Manis Jumbo": (60, 15)
    }
    for sku, (base_demand, std_dev) in products.items():
        for d in dates:
            # Efek akhir pekan (Jumat-Minggu naik 30%)
            weekend_boost = 1.3 if d.dayofweek in [4, 5, 6] else 1.0
            trend = (d - dates[0]).days * 0.03
            qty = max(1, int(np.random.normal(base_demand * weekend_boost + trend, std_dev)))
            data.append({"tanggal_transaksi": d, "nama_produk": sku, "jumlah_terjual": qty})
    return pd.DataFrame(data)

# --- SIDEBAR: INPUT & PARAMETER ---
st.sidebar.header("1. Sumber Data Transaksi")
uploaded_file = st.sidebar.file_uploader("Unggah file CSV atau Excel (.xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)
    st.sidebar.success("File berhasil dimuat!")
else:
    df_raw = generate_dummy_data()
    st.sidebar.info("Menggunakan data simulasi 6 bulan. Unggah file asli mitra Anda di atas.")

# Validasi & Pembersihan Kolom
required_cols = {'tanggal_transaksi', 'nama_produk', 'jumlah_terjual'}
if not required_cols.issubset(set(df_raw.columns)):
    st.error(f"Format kolom tidak sesuai! Pastikan file memiliki kolom: {', '.join(required_cols)}")
    st.stop()

df_raw['tanggal_transaksi'] = pd.to_datetime(df_raw['tanggal_transaksi'])

st.sidebar.header("2. Parameter Operasional Toko")
sku_list = df_raw['nama_produk'].unique().tolist()
selected_sku = st.sidebar.selectbox("Pilih Produk (SKU):", sku_list)
forecast_days = st.sidebar.slider("Jangka Waktu Prediksi (Hari ke depan):", 7, 30, 14)
lead_time = st.sidebar.number_input("Waktu Tunggu Supplier / Lead Time (Hari):", min_value=1, max_value=30, value=2)
safety_stock = st.sidebar.number_input("Batas Stok Aman / Safety Stock (Unit):", min_value=0, max_value=1000, value=15)
current_stock = st.sidebar.number_input("Sisa Stok Fisik Saat Ini (Unit):", min_value=0, max_value=10000, value=30)

# --- PEMROSESAN TIME SERIES PER PRODUK ---
df_sku = df_raw[df_raw['nama_produk'] == selected_sku].copy()
daily_sales = df_sku.groupby('tanggal_transaksi')['jumlah_terjual'].sum().reset_index()

# Lengkapi tanggal yang kosong (hari tutup/0 penjualan)
full_idx = pd.date_range(start=daily_sales['tanggal_transaksi'].min(), end=daily_sales['tanggal_transaksi'].max())
daily_sales = daily_sales.set_index('tanggal_transaksi').reindex(full_idx, fill_value=0).reset_index()
daily_sales.columns = ['tanggal', 'terjual']

# --- REKAYASA FITUR (TREN + HARI DALAM SEMINGGU) ---
def build_features(dates_series, start_date):
    days_elapsed = (dates_series - start_date).dt.days.values.astype(float)
    dow = dates_series.dt.dayofweek.values
    # One-hot encoding hari Senin-Minggu (0-6)
    dow_ohe = np.eye(7)[dow]
    return np.column_stack([np.ones(len(dates_series)), days_elapsed, dow_ohe])

start_dt = daily_sales['tanggal'].min()
X_all = build_features(daily_sales['tanggal'], start_dt)
y_all = daily_sales['terjual'].values.astype(float)

# --- EVALUASI MODEL (TIME-BASED SPLIT 80:20) ---
split_idx = int(len(daily_sales) * 0.8)
X_train, y_train = X_all[:split_idx], y_all[:split_idx]
X_val, y_val = X_all[split_idx:], y_all[split_idx:]

theta_val, _, _, _ = np.linalg.lstsq(X_train, y_train, rcond=None)
val_preds = np.maximum(0, X_val @ theta_val)

# Hitung metrik MAE & WAPE (lebih stabil daripada MAPE saat ada angka 0)
mae = np.mean(np.abs(y_val - val_preds))
wape = (np.sum(np.abs(y_val - val_preds)) / max(1, np.sum(y_val))) * 100

# --- LATIH ULANG PADA SELURUH DATA & PREDIKSI KE DEPAN ---
theta_full, _, _, _ = np.linalg.lstsq(X_all, y_all, rcond=None)

last_date = daily_sales['tanggal'].max()
future_dates = pd.Series([last_date + timedelta(days=i) for i in range(1, forecast_days + 1)])
X_future = build_features(future_dates, start_dt)
future_preds = np.maximum(0, np.round(X_future @ theta_full)).astype(int)

df_forecast = pd.DataFrame({
    'tanggal': future_dates,
    'prediksi_terjual': future_preds
})

# --- KALKULASI REKOMENDASI RESTOCK ---
avg_daily_pred = df_forecast['prediksi_terjual'].mean()
demand_during_lead_time = int(np.ceil(avg_daily_pred * lead_time))
reorder_point = demand_during_lead_time + safety_stock
total_forecast_demand = int(df_forecast['prediksi_terjual'].sum())
recommended_order = max(0, (total_forecast_demand + safety_stock) - current_stock)

# --- TAMPILAN DASHBOARD UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Prediksi Permintaan Total", f"{total_forecast_demand} unit", f"Untuk {forecast_days} hari")
col2.metric("Titik Pesan Ulang (ROP)", f"{reorder_point} unit", f"Lead time {lead_time} hari")
col3.metric("Saran Jumlah Kulakan", f"{recommended_order} unit", "Status: Segera Pesan" if current_stock <= reorder_point else "Status: Stok Aman")
col4.metric("Akurasi Uji (WAPE / MAE)", f"{wape:.1f}%", f"± {mae:.1f} unit/hari")

if current_stock <= reorder_point:
    st.warning(f"⚠️ **Peringatan Stok Menipis:** Sisa stok ({current_stock} unit) sudah berada di bawah Titik Pesan Ulang ({reorder_point} unit). Disarankan segera memesan **{recommended_order} unit**.")
else:
    st.success(f"✅ **Stok Aman:** Sisa stok ({current_stock} unit) masih mencukupi hingga batas Titik Pesan Ulang ({reorder_point} unit).")

# --- GRAFIK INTERAKTIF ---
st.subheader(f"📈 Grafik Historis & Prediksi Permintaan: {selected_sku}")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=daily_sales['tanggal'].tail(60),
    y=daily_sales['terjual'].tail(60),
    mode='lines+markers',
    name='Penjualan Aktual (60 Hari Terakhir)',
    line=dict(color='#3b82f6', width=2)
))
fig.add_trace(go.Scatter(
    x=df_forecast['tanggal'],
    y=df_forecast['prediksi_terjual'],
    mode='lines+markers',
    name=f'Prediksi {forecast_days} Hari Ke Depan',
    line=dict(color='#f97316', width=2, dash='dash')
))
fig.update_layout(xaxis_title="Tanggal", yaxis_title="Jumlah Terjual (Unit)", hovermode="x unified", height=420)
st.plotly_chart(fig, use_container_width=True)

# --- TABEL & UNDUH HASIL ---
with st.expander("📋 Lihat Tabel Rincian Prediksi Harian"):
    df_display = df_forecast.copy()
    df_display['tanggal'] = df_display['tanggal'].dt.strftime('%Y-%m-%d (%A)')
    st.dataframe(df_display, use_container_width=True)
    csv_export = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Unduh Jadwal Prediksi (.CSV)",
        data=csv_export,
        file_name=f"prediksi_restock_{selected_sku.replace(' ', '_')}.csv",
        mime="text/csv"
    )
