import pandas as pd
import os
from datetime import datetime, timedelta
import glob

def jalankan_proses_sales(config_path, output_path, mode_prod, val_prod, mode_toko, val_toko, tgl_awal_str, tgl_akhir_str, callback_log):
    base_path = config_path
    if not base_path.endswith("\\"):
        base_path += "\\"

    if not tgl_awal_str or not tgl_akhir_str:
        raise ValueError("Tanggal awal dan akhir harus diisi!")

    tgl_awal = datetime.strptime(tgl_awal_str, "%Y-%m-%d").date()
    tgl_akhir = datetime.strptime(tgl_akhir_str, "%Y-%m-%d").date()

    # --- 1. FILTER PRODUK ---
    list_produk = []  # Gunakan list_produk agar konsisten
    single_prdcd = None
    
    if mode_prod == "1 Produk (Ketik)":
        if not val_prod:
            raise ValueError("Kode Produk (PRDCD) harus diisi!")
        single_prdcd = val_prod.strip()
        
    elif mode_prod == "Banyak Produk (Excel)" and val_prod != "":
        if os.path.exists(val_prod):
            try:
                # Membaca file Excel menggunakan Pandas
                df_filter_prod = pd.read_excel(val_prod, dtype=str)
                
                # Ambil kolom pertama sebagai daftar kode produk (PLU/PRDCD)
                kolom_pertama = df_filter_prod.columns[0]
                list_produk = df_filter_prod[kolom_pertama].dropna().str.strip().tolist()
                
                callback_log(f"  -> Berhasil memuat {len(list_produk)} produk dari file Excel.")
            except Exception as e:
                callback_log(f"  -> ERROR membaca file Excel produk: {str(e)}")
        else:
            callback_log(f"  -> PERINGATAN: File Excel produk tidak ditemukan di {val_prod}")

    # --- 2. DAFTAR TOKO ---
    list_toko_kode = []
    if mode_toko == "1 Toko (Ketik)":
        if not val_toko:
            raise ValueError("Kode Toko harus diisi!")
        list_toko_kode.append(val_toko.strip())
        
    elif mode_toko in ["Banyak Toko (Excel)", "Banyak Toko (CSV)"]:
        if not val_toko or not os.path.exists(val_toko):
            raise ValueError("File daftar toko belum dipilih atau tidak valid!")
        
        try:
            # Deteksi otomatis apakah file Excel atau CSV
            if val_toko.lower().endswith(('.xlsx', '.xls')):
                df_toko_master = pd.read_excel(val_toko, dtype=str)
            else:
                df_toko_master = pd.read_csv(val_toko, dtype=str, on_bad_lines='skip')
                
            df_toko_master.columns = df_toko_master.columns.str.lower().str.strip()
            
            # Cari nama kolom yang sesuai secara fleksibel
            kolom_toko = None
            for col in ['toko', 'kdtk', 'store', 'kode_toko']:
                if col in df_toko_master.columns:
                    kolom_toko = col
                    break
            
            if kolom_toko is None:
                kolom_toko = df_toko_master.columns[0]
                
            list_toko_kode = df_toko_master[kolom_toko].dropna().astype(str).str.strip().tolist()
            callback_log(f"  -> Berhasil memuat {len(list_toko_kode)} daftar toko dari file.")
        except Exception as e:
            raise ValueError(f"Gagal membaca file daftar toko: {str(e)}")
            
    data_gabungan = []
    current_date = tgl_awal
    
    while current_date <= tgl_akhir:
        bln_str = current_date.strftime("%m")  # Bulan (MM)
        tgl_str = current_date.strftime("%d")  # Tanggal (dd)
        
        if mode_toko == "Semua Toko":
            pola_pencarian = f"{base_path}DT{bln_str}{tgl_str}*.??*"
            files_ditemukan = glob.glob(pola_pencarian)
            
            for nama_file in files_ditemukan:
                try:
                    if os.path.exists(nama_file):
                        callback_log(f"Membaca file {nama_file}")
                        df_harian = pd.read_csv(nama_file, sep='|', encoding='latin-1', engine='python', on_bad_lines='skip')
                        df_harian.columns = df_harian.columns.str.lower().str.strip()
                        
                        if 'prdcd' not in df_harian.columns:
                            continue
                            
                        df_harian['prdcd'] = df_harian['prdcd'].astype(str).str.strip()
                        
                        # Penanganan kolom toko / shop
                        if 'toko' not in df_harian.columns:
                            if 'shop' in df_harian.columns:
                                df_harian['toko'] = df_harian['shop'].astype(str).str.strip()
                            else:
                                df_harian['toko'] = "UNKNOWN"
                        else:
                            df_harian['toko'] = df_harian['toko'].astype(str).str.strip()
                        
                        # Filter Produk (Disesuaikan dengan "Banyak Produk (Excel)")
                        if mode_prod == "1 Produk (Ketik)":
                            df_filter = df_harian[df_harian['prdcd'] == single_prdcd]
                        elif mode_prod == "Banyak Produk (Excel)":
                            df_filter = df_harian[df_harian['prdcd'].isin(list_produk)]
                        else: 
                            df_filter = df_harian
                            
                        if not df_filter.empty:
                            df_filter['tanggal'] = current_date
                            data_gabungan.append(df_filter)
                except Exception as file_err:
                    callback_log(f"⚠️ PERINGATAN / ERROR pada file {nama_file}: {str(file_err)}")
        else:
            for tk_code in list_toko_kode:
                tk_str = str(tk_code).strip()
                if len(tk_str) >= 4:
                    nama_file = f"{base_path}DT{bln_str}{tgl_str}{tk_str[0]}.{tk_str[-3:]}"
                else:
                    nama_file = f"{base_path}DT{bln_str}{tgl_str}{tk_str}"
                
                try:
                    if os.path.exists(nama_file):
                        callback_log(f"Membaca file {nama_file}")
                        df_harian = pd.read_csv(nama_file, sep='|', encoding='latin-1', engine='python', on_bad_lines='skip')
                        df_harian.columns = df_harian.columns.str.lower().str.strip()
                        
                        if 'prdcd' not in df_harian.columns:
                            continue
                            
                        df_harian['prdcd'] = df_harian['prdcd'].astype(str).str.strip()
                        
                        # Penanganan kolom toko / shop
                        if 'toko' not in df_harian.columns:
                            if 'shop' in df_harian.columns:
                                df_harian['toko'] = df_harian['shop'].astype(str).str.strip()
                            else:
                                df_harian['toko'] = tk_str
                        else:
                            df_harian['toko'] = df_harian['toko'].astype(str).str.strip()
                        
                        # Filter Produk (Disesuaikan dengan "Banyak Produk (Excel)")
                        if mode_prod == "1 Produk (Ketik)":
                            df_filter = df_harian[df_harian['prdcd'] == single_prdcd]
                        elif mode_prod == "Banyak Produk (Excel)":
                            df_filter = df_harian[df_harian['prdcd'].isin(list_produk)]
                        else: 
                            df_filter = df_harian
                            
                        if not df_filter.empty:
                            df_filter['tanggal'] = current_date
                            data_gabungan.append(df_filter)
                except Exception as file_err:
                    callback_log(f"⚠️ PERINGATAN / ERROR pada file {nama_file}: {str(file_err)}")
                    
        current_date += timedelta(days=1)

    if data_gabungan:
        callback_log("Menyatukan data dan melakukan kalkulasi Sales...")
        sdt = pd.concat(data_gabungan, ignore_index=True)
        
        # Konversi dan Kalkulasi
        sdt['hpp'] = pd.to_numeric(sdt['hpp'], errors='coerce').fillna(0)
        sdt['qty'] = pd.to_numeric(sdt['qty'], errors='coerce').fillna(0)
        sdt['gross'] = pd.to_numeric(sdt['gross'], errors='coerce').fillna(0)
        sdt['ppn'] = pd.to_numeric(sdt['ppn'], errors='coerce').fillna(0)
        
        sdt['slshpp'] = sdt['hpp'] * sdt['qty']
        sdt['bersih'] = sdt['gross'] - sdt['ppn']
        sdt['margin'] = sdt['bersih'] - sdt['slshpp']
        
        
        # Pastikan folder output ada, jika tidak buat otomatis
        os.makedirs(output_path, exist_ok=True)
        
        file_excel = os.path.join(output_path, "Sales.xlsx") # Sesuaikan nama file per modul
        file_csv = os.path.join(output_path, "Sales.csv")    # Sesuaikan nama file per modul
        
        #callback_log(f"Kolom yang tersedia: {list(sdt.columns)}")
        # --- TAMBAHAN FILTER QTY != 0 ---
        callback_log("Memfilter data (mengabaikan baris dengan nilai QTY = 0)...")
        # Pastikan nama kolom 'QTY' diketik sesuai dengan nama asli di data Anda (huruf besar/kecilnya berpengaruh)
        sdt = sdt[sdt['qty'] != 0] 
        # --------------------------------
        
        # 1. Selalu simpan ke CSV karena tidak ada batas maksimal baris
        callback_log("Menyimpan ke format CSV (aman untuk Big Data)...")
        sdt.to_csv(file_csv, index=False, sep='|') 
        
        # 2. Cek jumlah baris sebelum memproses Excel
        max_excel_rows = 1048500
        total_baris = len(sdt) 
        
        if total_baris <= max_excel_rows:
            callback_log(f"Menyimpan ke format Excel ({total_baris} baris)...")
            sdt.to_excel(file_excel, index=False)
            callback_log(f"SUKSES: File CSV dan Excel berhasil dibuat di:\n{output_path}")
        else:
            callback_log(f"INFO: Ukuran data ({total_baris} baris) melebihi batas limit Excel!")
            callback_log(f"SUKSES: File hanya diekspor ke format CSV di:\n{output_path}")
            
        return True
    else:
        callback_log("PERINGATAN: Tidak ada data ditemukan pada rentang tanggal tersebut!")
        return False