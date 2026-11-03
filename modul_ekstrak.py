import os
import zipfile
from datetime import datetime, timedelta

def jalankan_proses_ekstrak(path_mentah, path_prodmast, path_sales, path_stock, path_bpb, tgl_awal_str, tgl_akhir_str, callback_log):
    """
    Mesin Ekstrak Python (Pengganti PKUNZIP FoxPro)
    Membaca pola HR/FR + YYMMDD + .XXX (Kode Toko) lalu mendistribusikan isinya.
    """
    try:
        tgl_awal = datetime.strptime(tgl_awal_str, "%Y-%m-%d")
        tgl_akhir = datetime.strptime(tgl_akhir_str, "%Y-%m-%d")
    except ValueError:
        callback_log("ERROR: Format tanggal salah (Gunakan YYYY-MM-DD).")
        return False

    if not os.path.exists(path_mentah):
        callback_log(f"ERROR: Folder sumber RAW (ZIP/RAR) tidak ditemukan:\n{path_mentah}")
        return False

    delta = tgl_akhir - tgl_awal
    file_ditemukan = False

    callback_log(f"Memindai direktori: {path_mentah}")

    for i in range(delta.days + 1):
        tgl_target = tgl_awal + timedelta(days=i)
        
        # Konversi ke format penamaan Indomaret
        tgl_pola = tgl_target.strftime("%y%m%d")   # Contoh: 261014 untuk pencarian nama file luar
        bulan_hari = tgl_target.strftime("%m%d")   # Contoh: 1014 untuk pencarian nama file dalam (PR1014, DT1014)

        # Cari semua file di folder E:\HARIAN\RAW\
        for nama_file in os.listdir(path_mentah):
            nama_file_upper = nama_file.upper()
            
            # Filter file dengan pola HR261014, FR261014, dll
            if tgl_pola in nama_file_upper and (nama_file_upper.startswith('HR') or nama_file_upper.startswith('FR')):
                path_file_lengkap = os.path.join(path_mentah, nama_file)
                
                # Cek apakah file tersebut benar-benar ZIP (mengabaikan ekstensi kode toko .28W dsb)
                if zipfile.is_zipfile(path_file_lengkap):
                    file_ditemukan = True
                    callback_log(f"Membongkar arsip: {nama_file}...")
                    
                    try:
                        with zipfile.ZipFile(path_file_lengkap, 'r') as zip_ref:
                            for file_dalam_zip in zip_ref.namelist():
                                nama_huruf_kecil = file_dalam_zip.lower()
                                
                                # --- DISTRIBUSI OTOMATIS KE MASING-MASING FOLDER ---
                                # PR -> Masuk ke Folder Prodmast (XPR)
                                if nama_huruf_kecil.startswith(f"pr{bulan_hari}"):
                                    zip_ref.extract(file_dalam_zip, path_prodmast)
                                
                                # DT & PL -> Masuk ke Folder Sales 
                                # (Pembersihan SLS_QTY=0 akan dilakukan nanti oleh Pandas di modul_sales)
                                elif nama_huruf_kecil.startswith(f"dt{bulan_hari}") or nama_huruf_kecil.startswith(f"pl{bulan_hari}"):
                                    zip_ref.extract(file_dalam_zip, path_sales)
                                
                                # ST -> Masuk ke Folder Stock
                                elif nama_huruf_kecil.startswith(f"st{bulan_hari}"):
                                    zip_ref.extract(file_dalam_zip, path_stock)
                                
                                # WT / BPB -> Masuk ke Folder BPB & Retur
                                elif nama_huruf_kecil.startswith(f"wt{bulan_hari}") or nama_huruf_kecil.startswith("bpb"):
                                    zip_ref.extract(file_dalam_zip, path_bpb)
                                    
                    except Exception as e:
                        callback_log(f"  -> ERROR pada {nama_file}: {str(e)}")

    if not file_ditemukan:
        callback_log(f"PERINGATAN: Tidak ada file HR/FR yang cocok untuk rentang {tgl_awal_str} s/d {tgl_akhir_str}.")
        return False
        
    callback_log("-" * 40)
    callback_log("SUKSES: Seluruh data selesai diekstrak dan didistribusikan ke folder masing-masing.")
    return True