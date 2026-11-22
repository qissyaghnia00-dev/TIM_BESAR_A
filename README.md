# 📦 Peramal Penjualan & Rekomendasi Restock UMKM (Produk A)

Aplikasi web berbasis *Machine Learning* untuk membantu pelaku UMKM memprediksi permintaan produk di masa depan (*Sales Forecasting*) dan menghitung jumlah pembelian ulang barang yang optimal (*Inventory Restock Recommendation*).

Proyek ini dikembangkan untuk memenuhi tugas mata kuliah **AI untuk Solusi Bisnis dan Machine Learning**, Program Studi Sistem Informasi.

---

## 👥 Pembagian Peran Tim (Kelompok A)
* **Tim Data & Domain:** `[Nama Anggota 1]`, `[Nama Anggota 2]` *(Akuisisi data mitra, pembersihan data, anonimisasi UU PDP, Data Dictionary)*
* **Tim Model & Evaluasi:** `[Nama Anggota 3]`, `[Nama Anggota 4]` *(Feature engineering, pelatihan model Random Forest, evaluasi metrik error)*
* **Tim Pengembang & Integrasi:** `[Nama Anggota 5]`, `[Nama Anggota 6]` *(Pengembangan antarmuka Streamlit, integrasi logika restock, manajemen GitHub)*
* **Tim Penguji & Dokumentasi:** `[Nama Anggota 7]`, `[Nama Anggota 8]` *(Pengujian independen pada hold-out data, UAT mitra, penyusunan laporan akhir)*

---

## 🛠️ Fitur Utama Aplikasi
1. **Unggah Data Fleksibel:** Mendukung input riwayat transaksi harian (`.csv` atau `.xlsx`) maupun mode data simulasi bawaan.
2. **Peramalan Deret Waktu (*Time-Series Forecasting*):** Menggunakan algoritma *Random Forest Regressor* untuk membaca pola harian, akhir pekan (*weekend*), dan siklus tanggal bulanan.
3. **Kalkulasi Rekomendasi Restock Otomatis:** Menghitung saran belanja barang berdasarkan prediksi permintaan, sisa stok fisik terkini, waktu tunggu pengiriman (*lead time*), dan batas stok aman (*safety stock*).
4. **Visualisasi Tren Interaktif:** Grafik perbandingan penjualan aktual 60 hari terakhir dengan proyeksi 7–30 hari ke depan.

---

## 🚀 Cara Menjalankan Aplikasi di Komputer Lokal (VS Code)

1. **Clone repositori ini ke komputer Anda:**
   ```bash
   git clone https://github.com
   cd nama-repositori-anda
   ```

2. **Instal seluruh pustaka (*library*) yang dibutuhkan:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi Streamlit:**
   ```bash
   streamlit run app.py
   ```

4. Aplikasi akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

---

## 🔒 Catatan Privasi & Keamanan Data
Sesuai dengan prinsip pelindungan data pribadi (UU PDP), seluruh dataset transaksi riil milik mitra UMKM yang digunakan dalam pengembangan dan pengujian sistem ini **tidak diunggah ke repositori publik ini** dan telah melalui proses anonimisasi.