import os
import pandas as pd
from datetime import datetime, timedelta

def jalankan_proses_retur(config_path, output_path, mode_prod, val_prod, mode_toko, val_toko, tgl_awal_str, tgl_akhir_str, callback_log):
    """
    Modul untuk memproses data RETUR dari file WT.
    Filter utama: RTYPE != 'B'
    Mendukung input 1 Toko/Produk (Ketik) maupun Banyak Toko/Produk (Excel/CSV).
    """
    try:
        tgl_awal = datetime.strptime(tgl_awal_str, "%Y-%m-%d")
        tgl_akhir = datetime.strptime(tgl_akhir_str, "%Y-%m-%d")
    except ValueError:
        callback_log("ERROR: Format tanggal salah. Gunakan YYYY-MM-DD.")
        return False

    if not os.path.exists(config_path):
        callback_log(f"ERROR: Folder Retur tidak ditemukan di {config_path}")
        return False

    # --- 1. FILTER PRODUK (Mendukung Excel, CSV, & Ketik) ---
    list_prdcd = []
    single_prdcd = None
    
    if mode_prod == "1 Produk (Ketik)":
        if not val_prod:
            raise ValueError("Kode Produk (PRDCD) harus diisi!")
        single_prdcd = val_prod.strip()
        
    elif mode_prod in ["Banyak Produk (Excel)", "Banyak Produk (CSV)"]:
        if not val_prod or not os.path.exists(val_prod):
            raise ValueError("File daftar produk belum dipilih atau tidak valid!")
        try:
            if val_prod.lower().endswith(('.xlsx', '.xls')):
                df_prod_master = pd.read_excel(val_prod, dtype=str)
            else:
                df_prod_master = pd.read_csv(val_prod, dtype=str, on_bad_lines='skip')
                
            df_prod_master.columns = df_prod_master.columns.str.lower().str.strip()
            kolom_prod = next((col for col in ['prdcd', 'plu', 'kode_produk', 'produk'] if col in df_prod_master.columns), df_prod_master.columns[0])
            list_prdcd = df_prod_master[kolom_prod].dropna().astype(str).str.strip().tolist()
            callback_log(f"  -> Berhasil memuat {len(list_prdcd)} produk dari file.")
        except Exception as e:
            raise ValueError(f"Gagal membaca file daftar produk: {str(e)}")

    # --- 2. DAFTAR TOKO (Mendukung Excel, CSV, & Ketik) ---
    list_toko_kode = []
    if mode_toko == "1 Toko (Ketik)":
        if not val_toko:
            raise ValueError("Kode Toko harus diisi!")
        list_toko_kode.append(val_toko.strip())
        
    elif mode_toko in ["Banyak Toko (Excel)", "Banyak Toko (CSV)"]:
        if not val_toko or not os.path.exists(val_toko):
            raise ValueError("File daftar toko belum dipilih atau tidak valid!")
        try:
            if val_toko.lower().endswith(('.xlsx', '.xls')):
                df_toko_master = pd.read_excel(val_toko, dtype=str)
            else:
                df_toko_master = pd.read_csv(val_toko, dtype=str, on_bad_lines='skip')
                
            df_toko_master.columns = df_toko_master.columns.str.lower().str.strip()
            kolom_toko = next((col for col in ['toko', 'kdtk', 'store', 'kode_toko'] if col in df_toko_master.columns), df_toko_master.columns[0])
            list_toko_kode = df_toko_master[kolom_toko].dropna().astype(str).str.strip().tolist()
            callback_log(f"  -> Berhasil memuat {len(list_toko_kode)} toko dari file.")
        except Exception as e:
            raise ValueError(f"Gagal membaca file daftar toko: {str(e)}")

    delta = tgl_akhir - tgl_awal
    semua_data = []
    
    callback_log("Mulai membaca data WT untuk Retur (RTYPE selain 'B')...")

    for i in range(delta.days + 1):
        tgl_target = tgl_awal + timedelta(days=i)
        bulan_hari = tgl_target.strftime("%m%d")  
        
        for file_name in os.listdir(config_path):
            file_name_lower = file_name.lower()
            
            if file_name_lower.startswith(f"wt{bulan_hari}"):
                file_path = os.path.join(config_path, file_name)
                try:
                    df = pd.read_csv(file_path, sep='|', dtype=str, on_bad_lines='skip') 
                    
                    df.columns = df.columns.str.upper().str.strip()
                    
                    # ==========================================
                    # 1. FILTER UTAMA RETUR (RTYPE != 'B')
                    # ==========================================
                    if 'RTYPE' in df.columns:
                        df = df[df['RTYPE'].astype(str).str.upper().str.strip() != 'B']
                    else:
                        callback_log(f"PERINGATAN: Kolom 'RTYPE' tidak ditemukan di {file_name}")
                        continue
                        
                    if 'QTY' in df.columns:
                        df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce').fillna(0)
                        df = df[df['QTY'] != 0]

                    # ==========================================
                    # 2. FILTER TOKO (Aman Huruf Besar/Kecil)
                    # ==========================================
                    if mode_toko == "1 Toko (Ketik)" and val_toko != "":
                        if 'SHOP' in df.columns: 
                            df = df[df['SHOP'].astype(str).str.upper().str.strip() == val_toko.strip().upper()]
                    elif mode_toko in ["Banyak Toko (Excel)", "Banyak Toko (CSV)"]:
                        if 'SHOP' in df.columns:
                            list_toko_upper = [str(t).upper().strip() for t in list_toko_kode]
                            df = df[df['SHOP'].astype(str).str.upper().str.strip().isin(list_toko_upper)]

                    # ==========================================
                    # 3. FILTER PRODUK (Aman Huruf Besar/Kecil)
                    # ==========================================
                    if mode_prod == "1 Produk (Ketik)" and val_prod != "":
                        if 'PRDCD' in df.columns: 
                            df = df[df['PRDCD'].astype(str).str.upper().str.strip() == single_prdcd.strip().upper()]
                    elif mode_prod in ["Banyak Produk (Excel)", "Banyak Produk (CSV)"]:
                        if 'PRDCD' in df.columns:
                            list_prdcd_upper = [str(p).upper().strip() for p in list_prdcd]
                            df = df[df['PRDCD'].astype(str).str.upper().str.strip().isin(list_prdcd_upper)]

                    if not df.empty:
                        semua_data.append(df)
                        callback_log(f"  -> Membaca {file_name} ({len(df)} baris Retur)")

                except Exception as e:
                    callback_log(f"  -> Gagal memproses {file_name}: {str(e)}")

    if not semua_data:
        callback_log("PERINGATAN: Tidak ada data Retur yang ditemukan pada rentang tanggal & filter tersebut!")
        return False

    callback_log("Menyatukan semua data Retur...")
    df_final = pd.concat(semua_data, ignore_index=True)
    total_baris = len(df_final)

    os.makedirs(output_path, exist_ok=True)
    file_csv = os.path.join(output_path, "Hasil_Retur.csv")
    file_excel = os.path.join(output_path, "Hasil_Retur.xlsx")

    callback_log("Menyimpan ke format CSV...")
    df_final.to_csv(file_csv, index=False, sep='|')

    max_excel_rows = 1048500
    if total_baris <= max_excel_rows:
        callback_log(f"Menyimpan ke format Excel ({total_baris} baris)...")
        df_final.to_excel(file_excel, index=False)
        callback_log(f"SUKSES: File CSV dan Excel Retur berhasil dibuat di:\n{output_path}")
    else:
        callback_log(f"INFO: Ukuran data ({total_baris} baris) melebihi batas limit Excel!")
        callback_log(f"SUKSES: File hanya diekspor ke CSV di:\n{output_path}")

    return True