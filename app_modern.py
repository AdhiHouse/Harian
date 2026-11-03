import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import os
import threading
import json


# Import modul terpisah
from modul_ekstrak import jalankan_proses_ekstrak
from modul_prodmast import jalankan_proses_prodmast
from modul_sales import jalankan_proses_sales
from modul_stock import jalankan_proses_stock
from modul_bpb import jalankan_proses_bpb
from modul_retur import jalankan_proses_retur

# --- KONFIGURASI TEMA ---
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config_path.json"

class AppHSLPR(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Rekap Harian - Engine Versi 0.1")
        self.geometry("1150x700")
        
        self.load_config()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ====================================================================
        # SIDEBAR (TEMA: MODERN MOCHA)
        # ====================================================================
        WARNA_SIDEBAR = "#E6D5B8"      # Coklat muda krem (Latte)
        WARNA_TEKS = "#2E211B"         # Coklat tua pekat (Espresso) untuk teks
        WARNA_HOVER = "#D7C4A5"        # Coklat muda sedikit lebih gelap untuk efek sentuh
        WARNA_TOMBOL_AKTIF = "#4A3B32" # Coklat gelap elegan untuk logo & tombol setting

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=WARNA_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        # Kotak Logo 'Y' dibuat coklat gelap dengan teks putih krem
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Y", font=ctk.CTkFont(size=30, weight="bold"), 
                                       fg_color=WARNA_TOMBOL_AKTIF, text_color="#F4F4F4", width=50, height=50, corner_radius=5)
        self.logo_label.grid(row=0, column=0, padx=(20, 5), pady=20, sticky="w")
        
        # Teks Judul
        self.logo_text = ctk.CTkLabel(self.sidebar_frame, text="HARIAN\nExplorer Engine", font=ctk.CTkFont(size=14, weight="bold"), text_color=WARNA_TEKS, justify="left")
        self.logo_text.grid(row=0, column=0, padx=(80, 20), pady=20, sticky="w")

        menus = [
            ("Dashboard", "dashboard"),
            ("Ekstrak Data", "ekstrak"),
            ("Proses Prodmast", "prodmast"),
            ("Proses Sales", "sales"),
            ("Proses Stock", "stock"),
            ("Proses BPB", "bpb"),
            ("Proses Retur", "retur")
        ]
        
        # Generator Tombol Menu
        for i, (text, key) in enumerate(menus, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=f"   {text}", 
                fg_color="transparent", 
                text_color=WARNA_TEKS,                 # Teks jadi gelap
                hover_color=WARNA_HOVER,               # Efek hover elegan
                font=ctk.CTkFont(size=13, weight="bold"), 
                anchor="w", 
                command=lambda k=key: self.tampilkan_halaman(k)
            )
            btn.grid(row=i, column=0, padx=20, pady=6, sticky="ew")

        # Tombol Setting di bawah
        self.btn_setting = ctk.CTkButton(
            self.sidebar_frame, 
            text="   ⚙ Setting Folder", 
            fg_color=WARNA_TOMBOL_AKTIF, 
            text_color="#F4F4F4", 
            hover_color="#2E211B",
            font=ctk.CTkFont(size=13, weight="bold"), 
            anchor="w", 
            command=lambda: self.tampilkan_halaman("setting")
        )
        self.btn_setting.grid(row=8, column=0, padx=20, pady=20, sticky="ew")

        # ====================================================================
        # MAIN CONTAINER
        # ====================================================================
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#F9F6F0")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        # Row 1 akan dipakai untuk halaman konten (Dashboard, Sales, dll)
        self.main_container.grid_rowconfigure(1, weight=1) 
        self.main_container.grid_columnconfigure(0, weight=1)

        # --- TAMBAHAN: Top Bar & Tombol Hamburger ---
        self.topbar = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent", height=50)
        self.topbar.grid(row=0, column=0, sticky="ew")
        
        # Tombol Hamburger
        self.btn_toggle = ctk.CTkButton(self.topbar, text="☰", width=40, height=40, fg_color="transparent", text_color="#2E211B", hover_color="#F4F4F4", font=ctk.CTkFont(size=24, weight="bold"), command=self.toggle_sidebar)
        self.btn_toggle.pack(side="left", padx=(20, 10), pady=10)
        
        # Sapaan di samping tombol
        tgl_sekarang = datetime.now().strftime("%d %B %Y")
        self.lbl_top_welcome = ctk.CTkLabel(self.topbar, text="Selamat Datang, Semangat BESTI!!!", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        self.lbl_top_welcome.pack(side="left", padx=5, pady=(12, 0))
        
        self.lbl_top_date = ctk.CTkLabel(self.topbar, text=f"|  Hari ini: {tgl_sekarang}", font=ctk.CTkFont(size=14), text_color="gray")
        self.lbl_top_date.pack(side="left", padx=10, pady=(16, 0))
        
        self.sidebar_visible = True
        # --------------------------------------------

        self.buat_halaman_dashboard()
        self.buat_halaman_ekstrak()
        self.buat_halaman_prodmast()
        self.buat_halaman_sales()
        self.buat_halaman_stock()
        self.buat_halaman_setting()
        self.buat_halaman_bpb()
        self.buat_halaman_retur()

        self.tampilkan_halaman("dashboard")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.path_ekstrak = data.get("path_ekstrak", "E:\\HARIAN\\RAW\\")
                    self.path_prodmast = data.get("path_prodmast", "E:\\HARIAN\\XPR\\")
                    self.path_sales = data.get("path_sales", "E:\\HARIAN\\DT\\")
                    self.path_stock = data.get("path_stock", "E:\\HARIAN\\ST\\")
                    self.path_bpb = data.get("path_bpb", "E:\\HARIAN\\BPB\\")
                    # Tambahkan default folder output (misal di drive D:)
                    self.path_output = data.get("path_output", "D:\\HASIL_REKAP\\") 
            except:
                self.path_ekstrak = "E:\\HARIAN\\RAW\\"
                self.path_prodmast = "E:\\HARIAN\\XPR\\"
                self.path_sales = "E:\\HARIAN\\DT\\"
                self.path_stock = "E:\\HARIAN\\ST\\"
                self.path_bpb = "E:\\HARIAN\\BPB\\"
                self.path_output = "D:\\HASIL_REKAP\\"
        else:
            self.path_ekstrak = "E:\\HARIAN\\RAW\\"
            self.path_prodmast = "E:\\HARIAN\\XPR\\"
            self.path_sales = "E:\\HARIAN\\DT\\"
            self.path_stock = "E:\\HARIAN\\ST\\"
            self.path_bpb = "E:\\HARIAN\\BPB\\"
            self.path_output = "D:\\HASIL_REKAP\\"

    def save_config(self):
        data = {
            "path_ekstrak": self.entry_path_ekstrak.get().strip(),
            "path_prodmast": self.entry_path_prodmast.get().strip(),
            "path_sales": self.entry_path_sales.get().strip(),
            "path_stock": self.entry_path_stock.get().strip(),
            "path_bpb": self.entry_path_bpb.get().strip(),
            "path_output": self.entry_path_output.get().strip()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
            
        # 1. Muat ulang konfigurasi ke variabel aplikasi
        self.load_config()
        
        # 2. Hancurkan frame dashboard yang lama dan buat ulang agar kartu menampilkan path terbaru
        if hasattr(self, 'frame_dashboard'):
            self.frame_dashboard.destroy()
        self.buat_halaman_dashboard()
        
        messagebox.showinfo("Sukses", "Pengaturan folder berhasil disimpan dan diperbarui!")
    
    def toggle_sidebar(self):
        if self.sidebar_visible:
            # Sembunyikan sidebar
            self.sidebar_frame.grid_forget()
            self.sidebar_visible = False
        else:
            # Tampilkan kembali sidebar
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.sidebar_visible = True
    
    def tampilkan_halaman(self, nama_halaman):
        # Pastikan self.frame_ekstrak dimasukkan ke dalam list di bawah ini
        for frame in [self.frame_dashboard, self.frame_ekstrak, self.frame_prodmast, self.frame_sales, self.frame_setting, self.frame_stock, self.frame_bpb, self.frame_retur]:
            frame.grid_forget()

        getattr(self, f"frame_{nama_halaman}").grid(row=1, column=0, sticky="nsew")

    def buat_halaman_dashboard(self):
        self.frame_dashboard = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_dashboard.grid_rowconfigure(1, weight=1)  # Geser weight ke area riwayat
        self.frame_dashboard.grid_columnconfigure(0, weight=1)

        # --- 1. KARTU STATUS FOLDER AKTIF (Dengan Hover & Tombol Pintasan) ---
        status_frame = ctk.CTkFrame(self.frame_dashboard, fg_color="transparent")
        status_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 15))
        status_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Tambahan parameter 'halaman_target' untuk navigasi
        def buat_kartu(master, col, judul, path_val, warna_asli, warna_hover, halaman_target):
            # Tinggi ditambah menjadi 115 untuk ruang tombol
            card = ctk.CTkFrame(master, fg_color=warna_asli, corner_radius=10, height=115, cursor="hand2")
            card.grid(row=0, column=col, sticky="nsew", padx=5)
            card.grid_propagate(False)
            
            lbl_judul = ctk.CTkLabel(card, text=judul, font=ctk.CTkFont(size=12, weight="bold"), text_color="white", cursor="hand2")
            lbl_judul.pack(pady=(12, 0), padx=10, anchor="w")
            
            lbl_path = ctk.CTkLabel(card, text=path_val, font=ctk.CTkFont(size=10), text_color="#E0E0E0", wraplength=140, justify="left", cursor="hand2")
            lbl_path.pack(pady=(2, 8), padx=10, anchor="w")

            # Tombol Pintasan di bawah teks
            btn_pintasan = ctk.CTkButton(
                card, text="Buka Modul ➔", 
                height=22, width=100, 
                fg_color="transparent", 
                border_width=1, border_color="white", text_color="white", 
                hover_color=warna_hover,
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda: self.tampilkan_halaman(halaman_target)
            )
            btn_pintasan.pack(side="bottom", pady=(0, 12), padx=10, anchor="w")

            # Efek Hover
            def on_enter(event):
                card.configure(fg_color=warna_hover)
                btn_pintasan.configure(fg_color=warna_asli) # Tombol ikut bereaksi
                
            def on_leave(event):
                card.configure(fg_color=warna_asli)
                btn_pintasan.configure(fg_color="transparent")

            # Fungsi Klik (Agar seluruh kartu bisa diklik, bukan cuma tombolnya)
            def aksi_klik(event):
                self.tampilkan_halaman(halaman_target)

            # Menerapkan Hover dan Klik ke semua elemen dalam kartu
            for widget in (card, lbl_judul, lbl_path):
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", aksi_klik)

        # Pembuatan 5 Kartu (Sematkan ID Halaman di argumen terakhir)
        buat_kartu(status_frame, 0, "📂 Prodmast", getattr(self, 'path_prodmast', '-'), "#5C4B41", "#705B4F", "prodmast") # Deep Espresso
        buat_kartu(status_frame, 1, "📂 Sales", getattr(self, 'path_sales', '-'), "#8B6D5C", "#A07F6C", "sales")       # Mocha
        buat_kartu(status_frame, 2, "📂 Stock", getattr(self, 'path_stock', '-'), "#657153", "#788564", "stock")       # Matcha / Olive
        buat_kartu(status_frame, 3, "📂 BPB & Retur", getattr(self, 'path_bpb', '-'), "#A26759", "#BA7767", "bpb")     # Terracotta
        buat_kartu(status_frame, 4, "💾 Output", getattr(self, 'path_output', '-'), "#4A585F", "#5B6C74", "setting")  # Slate / Blue-Grey

        # --- 2. PANEL RIWAYAT SESI ---
        history_frame = ctk.CTkFrame(self.frame_dashboard, fg_color="transparent")
        history_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(5, 30))
        history_frame.grid_rowconfigure(1, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        # Warna teks judul riwayat diubah ke coklat pekat (#2E211B)
        ctk.CTkLabel(history_frame, text="Riwayat Aktivitas Terakhir", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2E211B").grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.log_dashboard = ctk.CTkTextbox(history_frame, fg_color="#F4F4F4", text_color="#333333", corner_radius=10, font=ctk.CTkFont(size=13))
        self.log_dashboard.grid(row=1, column=0, sticky="nsew")
        
        waktu_buka = datetime.now().strftime("%H:%M:%S")
        self.log_dashboard.insert("0.0", f"[{waktu_buka}] Aplikasi Enterprise Engine berhasil dijalankan.\n[{waktu_buka}] Sistem siap memproses data...\n")
        self.log_dashboard.configure(state="disabled")

    def buat_halaman_setting(self):
        self.frame_setting = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_setting.grid_rowconfigure(1, weight=1)
        self.frame_setting.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_setting, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        title_label = ctk.CTkLabel(header_frame, text="Pengaturan Sumber Data (Directory Path)", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        title_label.pack(side="left")

        content_setting = ctk.CTkScrollableFrame(self.frame_setting, fg_color="#F4F4F4", corner_radius=10)
        content_setting.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        
        # --- PATH EKSTRAK (Satu sumber paling hulu) ---
        ctk.CTkLabel(content_setting, text="Folder File Mentah / Ekstrak (ZIP/RAR):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(anchor="w", padx=20, pady=(15, 2))
        self.entry_path_ekstrak = ctk.CTkEntry(content_setting, width=500, height=35, font=ctk.CTkFont(size=13))
        self.entry_path_ekstrak.pack(anchor="w", padx=20, pady=2)
        self.entry_path_ekstrak.insert(0, getattr(self, 'path_ekstrak', 'E:\\HARIAN\\RAW\\'))

        # Path Prodmast (Ubah sedikit pady-nya agar lebih hemat ruang)
        ctk.CTkLabel(content_setting, text="Folder Sumber Data Prodmast Toko (PR):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(anchor="w", padx=20, pady=(10, 2))
        self.entry_path_prodmast = ctk.CTkEntry(content_setting, width=500, height=35, font=ctk.CTkFont(size=13))
        self.entry_path_prodmast.pack(anchor="w", padx=20, pady=2)
        self.entry_path_prodmast.insert(0, self.path_prodmast)

        # Path Sales
        ctk.CTkLabel(content_setting, text="Folder Sumber Data Sales Toko (DT):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_path_sales = ctk.CTkEntry(content_setting, width=500, height=35, font=ctk.CTkFont(size=13))
        self.entry_path_sales.pack(anchor="w", padx=20, pady=5)
        self.entry_path_sales.insert(0, self.path_sales)
        
        # Path Stock ---
        ctk.CTkLabel(content_setting, text="Folder Sumber Data Stock Toko (ST):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_path_stock = ctk.CTkEntry(content_setting, width=500, height=35, font=ctk.CTkFont(size=13))
        self.entry_path_stock.pack(anchor="w", padx=20, pady=5)
        self.entry_path_stock.insert(0, self.path_stock)
        
        # --- PATH BPB & RETUR ---
        ctk.CTkLabel(content_setting, text="Folder Sumber Data BPB & Retur:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_path_bpb = ctk.CTkEntry(content_setting, width=500, height=35, font=ctk.CTkFont(size=13))
        self.entry_path_bpb.pack(anchor="w", padx=20, pady=5)
        self.entry_path_bpb.insert(0, getattr(self, 'path_bpb', 'E:\\HARIAN\\BPB\\'))
        
        # Path Output ---
        ctk.CTkLabel(content_setting, text="Folder Penyimpanan Hasil Export (Output):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2E211B").pack(anchor="w", padx=20, pady=(25, 5))
        self.entry_path_output = ctk.CTkEntry(content_setting, width=500, height=35, font=ctk.CTkFont(size=13))
        self.entry_path_output.pack(anchor="w", padx=20, pady=5)
        self.entry_path_output.insert(0, self.path_output)
        
        btn_simpan_setting = ctk.CTkButton(content_setting, text="Simpan Pengaturan", fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), width=160, height=35, command=self.save_config)
        btn_simpan_setting.pack(anchor="w", padx=20, pady=20)
        
    def buat_halaman_ekstrak(self):
        self.frame_ekstrak = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_ekstrak.grid_rowconfigure(2, weight=1)
        self.frame_ekstrak.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_ekstrak, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(header_frame, text="Proses Ekstrak Data (ZIP/RAR)", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        title_label.pack(side="left")
        
        status_btn = ctk.CTkButton(header_frame, text="Engine Ready", fg_color="#4A3B32", corner_radius=0, hover=False)
        status_btn.pack(side="right")

        self.control_frame_ekstrak = ctk.CTkFrame(self.frame_ekstrak, corner_radius=0, fg_color="#4A3B32")
        self.control_frame_ekstrak.grid(row=1, column=0, sticky="ew", padx=20, pady=5)

        ctk.CTkLabel(self.control_frame_ekstrak, text="TGL AWAL (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_ekstrak, text="TGL AKHIR (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")

        self.entry_tgl_awal_ekstrak = ctk.CTkEntry(self.control_frame_ekstrak, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_awal_ekstrak.grid(row=1, column=0, padx=15, pady=5)
        self.entry_tgl_awal_ekstrak.insert(0, "2026-10-14")
        
        self.entry_tgl_akhir_ekstrak = ctk.CTkEntry(self.control_frame_ekstrak, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_akhir_ekstrak.grid(row=1, column=1, padx=15, pady=5)
        self.entry_tgl_akhir_ekstrak.insert(0, "2026-10-15")

        btn_frame = ctk.CTkFrame(self.control_frame_ekstrak, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 15))

        self.btn_proses_ekstrak = ctk.CTkButton(btn_frame, text="↓ PROSES EKSTRAK", width=180, fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), corner_radius=0, command=self.mulai_proses_ekstrak)
        self.btn_proses_ekstrak.pack(side="left")

        self.log_area_ekstrak = ctk.CTkTextbox(self.frame_ekstrak, fg_color="#1B1410", text_color="white", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area_ekstrak.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)
        self.log_area_ekstrak.insert("0.0", "--- LOG PROSES EKSTRAK AKAN MUNCUL DI SINI ---\n\n")

    def catat_log_ekstrak(self, pesan):
        self.log_area_ekstrak.insert("end", pesan + "\n")
        self.log_area_ekstrak.see("end")

    def mulai_proses_ekstrak(self):
        import threading # Pastikan threading di-import di awal file
        threading.Thread(target=self.jalankan_thread_ekstrak, daemon=True).start()

    def jalankan_thread_ekstrak(self):
        from tkinter import messagebox
        try:
            self.btn_proses_ekstrak.configure(state="disabled", text="MEMPROSES...")
            self.catat_log_ekstrak("Memulai proses Ekstrak Data...")

            jalankan_proses_ekstrak(
                path_mentah=self.path_ekstrak,
                path_prodmast=self.path_prodmast,
                path_sales=self.path_sales,
                path_stock=self.path_stock,
                path_bpb=self.path_bpb,
                tgl_awal_str=self.entry_tgl_awal_ekstrak.get().strip(),
                tgl_akhir_str=self.entry_tgl_akhir_ekstrak.get().strip(),
                callback_log=self.catat_log_ekstrak
            )

            messagebox.showinfo("Sukses", "Proses Ekstrak dan Distribusi Selesai!")
            self.tambah_riwayat_dashboard("✅ Berhasil: Ekstraksi data mentah toko selesai didistribusikan.")
        except Exception as e:
            self.catat_log_ekstrak(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.btn_proses_ekstrak.configure(state="normal", text="↓ PROSES EKSTRAK")
        
    def buat_halaman_prodmast(self):
        self.frame_prodmast = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_prodmast.grid_rowconfigure(2, weight=1)
        self.frame_prodmast.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_prodmast, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(header_frame, text="Proses Prodmast Toko", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        title_label.pack(side="left")
        
        status_btn = ctk.CTkButton(header_frame, text="Engine Ready", fg_color="#4A3B32", corner_radius=0, hover=False)
        status_btn.pack(side="right")

        self.control_frame_prod = ctk.CTkFrame(self.frame_prodmast, corner_radius=0, fg_color="#4A3B32")
        self.control_frame_prod.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        ctk.CTkLabel(self.control_frame_prod, text="MODE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_prod, text="INPUT / FILE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_prod, text="MODE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_prod, text="INPUT / FILE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=15, pady=(15, 0), sticky="w")

        self.mode_produk_var = ctk.StringVar(value="1 Produk (Ketik)")
        self.dropdown_produk = ctk.CTkOptionMenu(self.control_frame_prod, values=["1 Produk (Ketik)", "Banyak Produk (Excel)", "Semua Produk"], 
                                                 variable=self.mode_produk_var, command=self.update_ui_produk, width=160, corner_radius=0)
        self.dropdown_produk.grid(row=1, column=0, padx=15, pady=5)

        self.container_input_produk = ctk.CTkFrame(self.control_frame_prod, fg_color="transparent")
        self.container_input_produk.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        self.entry_produk = ctk.CTkEntry(self.container_input_produk, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_produk.pack(side="left")
        
        self.btn_file_produk = ctk.CTkButton(self.container_input_produk, text="Pilih CSV", width=90, fg_color="#8B6D5C", corner_radius=0, command=lambda: self.pilih_file_csv(self.entry_produk))
        self.btn_file_produk.pack_forget() 

        self.mode_toko_var = ctk.StringVar(value="1 Toko (Ketik)")
        self.dropdown_toko = ctk.CTkOptionMenu(self.control_frame_prod, values=["1 Toko (Ketik)", "Banyak Toko (Excel)", "Semua Toko"], 
                                               variable=self.mode_toko_var, command=self.update_ui_toko, width=160, corner_radius=0)
        self.dropdown_toko.grid(row=1, column=2, padx=15, pady=5)

        self.container_input_toko = ctk.CTkFrame(self.control_frame_prod, fg_color="transparent")
        self.container_input_toko.grid(row=1, column=3, padx=15, pady=5, sticky="w")
        
        self.entry_toko = ctk.CTkEntry(self.container_input_toko, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_toko.pack(side="left")
        
        self.btn_file_toko = ctk.CTkButton(self.container_input_toko, text="Pilih CSV", width=90, fg_color="#8B6D5C", corner_radius=0, command=lambda: self.pilih_file_csv(self.entry_toko))
        self.btn_file_toko.pack_forget()

        ctk.CTkLabel(self.control_frame_prod, text="TGL AWAL (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=0, padx=15, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_prod, text="TGL AKHIR (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=1, padx=15, pady=(10, 0), sticky="w")

        self.entry_tgl_awal = ctk.CTkEntry(self.control_frame_prod, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_awal.grid(row=3, column=0, padx=15, pady=5)
        self.entry_tgl_awal.insert(0, "2026-10-14")
        
        self.entry_tgl_akhir = ctk.CTkEntry(self.control_frame_prod, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_akhir.grid(row=3, column=1, padx=15, pady=5)
        self.entry_tgl_akhir.insert(0, "2026-10-15")

        btn_frame = ctk.CTkFrame(self.control_frame_prod, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 15))

        self.btn_proses_prod = ctk.CTkButton(btn_frame, text="↓ PROSES PRODMAST", width=180, fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), corner_radius=0, command=self.mulai_proses_prodmast)
        self.btn_proses_prod.pack(side="left")

        self.log_area_prod = ctk.CTkTextbox(self.frame_prodmast, fg_color="#1B1410", text_color="white", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area_prod.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)
        self.log_area_prod.insert("0.0", "--- LOG PROSES PRODMAST AKAN MUNCUL DI SINI ---\n\n")

    def buat_halaman_sales(self):
        self.frame_sales = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_sales.grid_rowconfigure(2, weight=1)
        self.frame_sales.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_sales, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(header_frame, text="Proses Sales Cabang / Toko", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        title_label.pack(side="left")
        
        status_btn = ctk.CTkButton(header_frame, text="Engine Ready", fg_color="#4A3B32", corner_radius=0, hover=False)
        status_btn.pack(side="right")

        self.control_frame_sales = ctk.CTkFrame(self.frame_sales, corner_radius=0, fg_color="#4A3B32")
        self.control_frame_sales.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        ctk.CTkLabel(self.control_frame_sales, text="MODE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_sales, text="INPUT / FILE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_sales, text="MODE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_sales, text="INPUT / FILE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=15, pady=(15, 0), sticky="w")

        self.mode_produk_sales_var = ctk.StringVar(value="1 Produk (Ketik)")
        self.dropdown_produk_sales = ctk.CTkOptionMenu(self.control_frame_sales, values=["1 Produk (Ketik)", "Banyak Produk (Excel)", "Semua Produk"], 
                                                       variable=self.mode_produk_sales_var, command=self.update_ui_produk_sales, width=160, corner_radius=0)
        self.dropdown_produk_sales.grid(row=1, column=0, padx=15, pady=5)

        self.container_input_produk_sales = ctk.CTkFrame(self.control_frame_sales, fg_color="transparent")
        self.container_input_produk_sales.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        self.entry_produk_sales = ctk.CTkEntry(self.container_input_produk_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_produk_sales.pack(side="left")

        self.mode_toko_sales_var = ctk.StringVar(value="1 Toko (Ketik)")
        self.dropdown_toko_sales = ctk.CTkOptionMenu(self.control_frame_sales, values=["1 Toko (Ketik)", "Banyak Toko (Excel)", "Semua Toko"], 
                                                     variable=self.mode_toko_sales_var, command=self.update_ui_toko_sales, width=160, corner_radius=0)
        self.dropdown_toko_sales.grid(row=1, column=2, padx=15, pady=5)

        self.container_input_toko_sales = ctk.CTkFrame(self.control_frame_sales, fg_color="transparent")
        self.container_input_toko_sales.grid(row=1, column=3, padx=15, pady=5, sticky="w")
        
        self.entry_toko_sales = ctk.CTkEntry(self.container_input_toko_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_toko_sales.pack(side="left")

        ctk.CTkLabel(self.control_frame_sales, text="TGL AWAL (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=0, padx=15, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_sales, text="TGL AKHIR (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=1, padx=15, pady=(10, 0), sticky="w")

        self.entry_tgl_awal_sales = ctk.CTkEntry(self.control_frame_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_awal_sales.grid(row=3, column=0, padx=15, pady=5)
        self.entry_tgl_awal_sales.insert(0, "2026-10-14")
        
        self.entry_tgl_akhir_sales = ctk.CTkEntry(self.control_frame_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_akhir_sales.grid(row=3, column=1, padx=15, pady=5)
        self.entry_tgl_akhir_sales.insert(0, "2026-10-15")
        
        
        btn_frame_sales = ctk.CTkFrame(self.control_frame_sales, fg_color="transparent")
        btn_frame_sales.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 15))

        self.btn_proses_sales = ctk.CTkButton(btn_frame_sales, text="↓ PROSES SALES", width=180, fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), corner_radius=0, command=self.mulai_proses_sales)
        self.btn_proses_sales.pack(side="left")

        self.log_area_sales = ctk.CTkTextbox(self.frame_sales, fg_color="#1B1410", text_color="white", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area_sales.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)
        self.log_area_sales.insert("0.0", "--- LOG PROSES SALES AKAN MUNCUL DI SINI ---\n\n")

    def update_ui_produk(self, pilihan):
        for widget in self.container_input_produk.winfo_children():
            widget.pack_forget()
            
        if pilihan == "1 Produk (Ketik)":
            self.entry_produk = ctk.CTkEntry(self.container_input_produk, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk.pack(side="left")
        elif pilihan == "Banyak Produk (Excel)":
            self.entry_produk = ctk.CTkEntry(self.container_input_produk, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_produk, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_produk)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Produk":
            self.entry_produk = ctk.CTkEntry(self.container_input_produk, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk.insert(0, "(Semua Produk)")
            self.entry_produk.configure(state="disabled")
            self.entry_produk.pack(side="left")

    def update_ui_toko(self, pilihan):
        for widget in self.container_input_toko.winfo_children():
            widget.pack_forget()
            
        if pilihan == "1 Toko (Ketik)":
            self.entry_toko = ctk.CTkEntry(self.container_input_toko, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko.pack(side="left")
        elif pilihan == "Banyak Toko (Excel)":
            self.entry_toko = ctk.CTkEntry(self.container_input_toko, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_toko, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_toko)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Toko":
            self.entry_toko = ctk.CTkEntry(self.container_input_toko, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko.insert(0, "(Semua Toko / Otomatis)")
            self.entry_toko.configure(state="disabled")
            self.entry_toko.pack(side="left")

    def update_ui_produk_sales(self, pilihan):
        for widget in self.container_input_produk_sales.winfo_children():
            widget.pack_forget()
            
        if pilihan == "1 Produk (Ketik)":
            self.entry_produk_sales = ctk.CTkEntry(self.container_input_produk_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_sales.pack(side="left")
            
        elif pilihan == "Banyak Produk (Excel)":
            self.entry_produk_sales = ctk.CTkEntry(self.container_input_produk_sales, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_sales.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_produk_sales, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C", 
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_produk_sales)
            )
            btn_file.pack(side="left")
            
        elif pilihan == "Semua Produk":
            self.entry_produk_sales = ctk.CTkEntry(self.container_input_produk_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_sales.insert(0, "(Semua Produk)")
            self.entry_produk_sales.configure(state="disabled")
            self.entry_produk_sales.pack(side="left")

    def update_ui_toko_sales(self, pilihan):
        for widget in self.container_input_toko_sales.winfo_children():
            widget.destroy()
            
        if pilihan == "1 Toko (Ketik)":
            self.entry_toko_sales = ctk.CTkEntry(self.container_input_toko_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_sales.pack(side="left")
            
        elif pilihan == "Banyak Toko (Excel)":  # <-- Diubah dari CSV ke Excel
            self.entry_toko_sales = ctk.CTkEntry(self.container_input_toko_sales, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_sales.pack(side="left", padx=(0, 5))
            
            # Tombol pilih file Excel untuk daftar toko
            btn_file = ctk.CTkButton(
                self.container_input_toko_sales, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C",  # Warna Mocha yang serasi
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_toko_sales)
            )
            btn_file.pack(side="left")
            
        elif pilihan == "Semua Toko":
            self.entry_toko_sales = ctk.CTkEntry(self.container_input_toko_sales, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_sales.insert(0, "(Semua Toko)")
            self.entry_toko_sales.configure(state="disabled")
            self.entry_toko_sales.pack(side="left")

    def buat_halaman_kosong(self, nama_attr, teks_tengah):
        frame = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        label = ctk.CTkLabel(frame, text=teks_tengah, font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        label.place(relx=0.5, rely=0.5, anchor="center")
        setattr(self, f"frame_{nama_attr}", frame)

    def tambah_riwayat_dashboard(self, pesan):
        self.log_dashboard.configure(state="normal") # Buka gembok teks
        waktu = datetime.now().strftime("%H:%M:%S")
        self.log_dashboard.insert("end", f"[{waktu}] {pesan}\n")
        self.log_dashboard.see("end") # Scroll otomatis ke bawah
        self.log_dashboard.configure(state="disabled") # Gembok lagi
    
    def catat_log_prod(self, pesan):
        self.log_area_prod.insert("end", pesan + "\n")
        self.log_area_prod.see("end")

    def catat_log_sales(self, pesan):
        self.log_area_sales.insert("end", pesan + "\n")
        self.log_area_sales.see("end")

    def pilih_file_excel(self, entry_target):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Pilih File Daftar Produk (Excel)",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if file_path:
            entry_target.delete(0, "end")
            entry_target.insert(0, file_path)
    
    def pilih_file_csv(self, entry_widget):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            entry_widget.configure(state="normal")
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, filename)

    def mulai_proses_prodmast(self):
        threading.Thread(target=self.jalankan_thread_prodmast, daemon=True).start()

    def jalankan_thread_prodmast(self):
        try:
            self.btn_proses_prod.configure(state="disabled", text="MEMPROSES...")
            self.catat_log_prod("Memulai proses Prodmast...")

            jalankan_proses_prodmast(
                config_path=self.path_prodmast,
                output_path=self.path_output,
                mode_prod=self.mode_produk_var.get(),
                val_prod=self.entry_produk.get().strip(),
                mode_toko=self.mode_toko_var.get(),
                val_toko=self.entry_toko.get().strip(),
                tgl_awal_str=self.entry_tgl_awal.get().strip(),
                tgl_akhir_str=self.entry_tgl_akhir.get().strip(),
                callback_log=self.catat_log_prod
            )

            messagebox.showinfo("Sukses", "Proses Prodmast Selesai!")
            self.tambah_riwayat_dashboard("✅ Berhasil: Ekspor data Prodmast selesai dilakukan.")
        except Exception as e:
            self.catat_log_prod(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.btn_proses_prod.configure(state="normal", text="↓ PROSES PRODMAST")

    def mulai_proses_sales(self):
        threading.Thread(target=self.jalankan_thread_sales, daemon=True).start()

    def jalankan_thread_sales(self):
        try:
            self.btn_proses_sales.configure(state="disabled", text="MEMPROSES...")
            self.catat_log_sales("Memulai proses Sales...")

            jalankan_proses_sales(
                config_path=self.path_sales,
                output_path=self.path_output,
                mode_prod=self.mode_produk_sales_var.get(),
                val_prod=self.entry_produk_sales.get().strip(),
                mode_toko=self.mode_toko_sales_var.get(),
                val_toko=self.entry_toko_sales.get().strip(),
                tgl_awal_str=self.entry_tgl_awal_sales.get().strip(),
                tgl_akhir_str=self.entry_tgl_akhir_sales.get().strip(),
                callback_log=self.catat_log_sales
            )

            messagebox.showinfo("Sukses", "Proses Sales Selesai!")
            self.tambah_riwayat_dashboard("✅ Berhasil: Ekspor data Sales selesai dilakukan.")
        except Exception as e:
            self.catat_log_sales(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.btn_proses_sales.configure(state="normal", text="↓ PROSES SALES")
        
        
    def buat_halaman_stock(self):
        self.frame_stock = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_stock.grid_rowconfigure(2, weight=1)
        self.frame_stock.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_stock, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(header_frame, text="Proses Stock Cabang / Toko", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B")
        title_label.pack(side="left")
        
        status_btn = ctk.CTkButton(header_frame, text="Engine Ready", fg_color="#4A3B32", corner_radius=0, hover=False)
        status_btn.pack(side="right")

        self.control_frame_stock = ctk.CTkFrame(self.frame_stock, corner_radius=0, fg_color="#4A3B32")
        self.control_frame_stock.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        ctk.CTkLabel(self.control_frame_stock, text="MODE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_stock, text="INPUT / FILE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_stock, text="MODE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_stock, text="INPUT / FILE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=15, pady=(15, 0), sticky="w")

        self.mode_produk_stock_var = ctk.StringVar(value="1 Produk (Ketik)")
        self.dropdown_produk_stock = ctk.CTkOptionMenu(self.control_frame_stock, values=["1 Produk (Ketik)", "Banyak Produk (Excel)", "Semua Produk"], 
                                                       variable=self.mode_produk_stock_var, command=self.update_ui_produk_stock, width=160, corner_radius=0)
        self.dropdown_produk_stock.grid(row=1, column=0, padx=15, pady=5)

        self.container_input_produk_stock = ctk.CTkFrame(self.control_frame_stock, fg_color="transparent")
        self.container_input_produk_stock.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        self.entry_produk_stock = ctk.CTkEntry(self.container_input_produk_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_produk_stock.pack(side="left")

        self.mode_toko_stock_var = ctk.StringVar(value="1 Toko (Ketik)")
        self.dropdown_toko_stock = ctk.CTkOptionMenu(self.control_frame_stock, values=["1 Toko (Ketik)", "Banyak Toko (Excel)", "Semua Toko"], 
                                                     variable=self.mode_toko_stock_var, command=self.update_ui_toko_stock, width=160, corner_radius=0)
        self.dropdown_toko_stock.grid(row=1, column=2, padx=15, pady=5)

        self.container_input_toko_stock = ctk.CTkFrame(self.control_frame_stock, fg_color="transparent")
        self.container_input_toko_stock.grid(row=1, column=3, padx=15, pady=5, sticky="w")
        
        self.entry_toko_stock = ctk.CTkEntry(self.container_input_toko_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_toko_stock.pack(side="left")

        ctk.CTkLabel(self.control_frame_stock, text="TGL AWAL (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=0, padx=15, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_stock, text="TGL AKHIR (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=1, padx=15, pady=(10, 0), sticky="w")

        self.entry_tgl_awal_stock = ctk.CTkEntry(self.control_frame_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_awal_stock.grid(row=3, column=0, padx=15, pady=5)
        self.entry_tgl_awal_stock.insert(0, "2026-10-14")
        
        self.entry_tgl_akhir_stock = ctk.CTkEntry(self.control_frame_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_akhir_stock.grid(row=3, column=1, padx=15, pady=5)
        self.entry_tgl_akhir_stock.insert(0, "2026-10-15")

        btn_frame_stock = ctk.CTkFrame(self.control_frame_stock, fg_color="transparent")
        btn_frame_stock.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 15))

        self.btn_proses_stock = ctk.CTkButton(btn_frame_stock, text="↓ PROSES STOCK", width=180, fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), corner_radius=0, command=self.mulai_proses_stock)
        self.btn_proses_stock.pack(side="left")

        self.log_area_stock = ctk.CTkTextbox(self.frame_stock, fg_color="#1B1410", text_color="white", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area_stock.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)
        self.log_area_stock.insert("0.0", "--- LOG PROSES STOCK AKAN MUNCUL DI SINI ---\n\n")

    def update_ui_produk_stock(self, pilihan):
        for widget in self.container_input_produk_stock.winfo_children():
            widget.pack_forget()
            
        if pilihan == "1 Produk (Ketik)":
            self.entry_produk_stock = ctk.CTkEntry(self.container_input_produk_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_stock.pack(side="left")
        elif pilihan == "Banyak Produk (Excel)":
            self.entry_produk_stock = ctk.CTkEntry(self.container_input_produk_stock, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_stock.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_produk_stock, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C", 
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_produk_stock)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Produk":
            self.entry_produk_stock = ctk.CTkEntry(self.container_input_produk_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_stock.insert(0, "(Semua Produk)")
            self.entry_produk_stock.configure(state="disabled")
            self.entry_produk_stock.pack(side="left")

    def update_ui_toko_stock(self, pilihan):
        for widget in self.container_input_toko_stock.winfo_children():
            widget.pack_forget()
            
        if pilihan == "1 Toko (Ketik)":
            self.entry_toko_stock = ctk.CTkEntry(self.container_input_toko_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_stock.pack(side="left")
        elif pilihan == "Banyak Toko (Excel)":
            self.entry_toko_stock = ctk.CTkEntry(self.container_input_toko_stock, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_stock.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_toko_stock, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C", 
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_toko_stock)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Toko":
            self.entry_toko_stock = ctk.CTkEntry(self.container_input_toko_stock, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_stock.insert(0, "(Semua Toko / Otomatis)")
            self.entry_toko_stock.configure(state="disabled")
            self.entry_toko_stock.pack(side="left")

    def catat_log_stock(self, pesan):
        self.log_area_stock.insert("end", pesan + "\n")
        self.log_area_stock.see("end")

    def mulai_proses_stock(self):
        threading.Thread(target=self.jalankan_thread_stock, daemon=True).start()

    def jalankan_thread_stock(self):
        try:
            self.btn_proses_stock.configure(state="disabled", text="MEMPROSES...")
            self.catat_log_stock("Memulai proses Stock...")

            # Catatan: Kita gunakan path_sales sementara, jika Anda punya path folder khusus stock, bisa ditambahkan di load_config nanti
            jalankan_proses_stock(
                config_path=self.path_stock,
                output_path=self.path_output,
                mode_prod=self.mode_produk_stock_var.get(),
                val_prod=self.entry_produk_stock.get().strip(),
                mode_toko=self.mode_toko_stock_var.get(),
                val_toko=self.entry_toko_stock.get().strip(),
                tgl_awal_str=self.entry_tgl_awal_stock.get().strip(),
                tgl_akhir_str=self.entry_tgl_akhir_stock.get().strip(),
                callback_log=self.catat_log_stock
            )

            messagebox.showinfo("Sukses", "Proses Stock Selesai!")
            self.tambah_riwayat_dashboard("✅ Berhasil: Ekspor data Stock selesai dilakukan.")
        except Exception as e:
            self.catat_log_stock(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.btn_proses_stock.configure(state="normal", text="↓ PROSES STOCK")
            
            
    # ===================================================================================
    # UI MODUL BPB
    # ===================================================================================
    def buat_halaman_bpb(self):
        self.frame_bpb = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_bpb.grid_rowconfigure(2, weight=1)
        self.frame_bpb.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_bpb, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(header_frame, text="Proses BPB (Penerimaan Barang)", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B").pack(side="left")
        ctk.CTkButton(header_frame, text="Engine Ready", fg_color="#4A3B32", corner_radius=0, hover=False).pack(side="right")

        self.control_frame_bpb = ctk.CTkFrame(self.frame_bpb, corner_radius=0, fg_color="#4A3B32")
        self.control_frame_bpb.grid(row=1, column=0, sticky="ew", padx=20, pady=5)

        # Baris 1: Filter Produk dan Toko
        ctk.CTkLabel(self.control_frame_bpb, text="MODE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_bpb, text="INPUT / FILE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_bpb, text="MODE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_bpb, text="INPUT / FILE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=15, pady=(15, 0), sticky="w")

        self.mode_produk_bpb_var = ctk.StringVar(value="1 Produk (Ketik)")
        self.dropdown_produk_bpb = ctk.CTkOptionMenu(self.control_frame_bpb, values=["1 Produk (Ketik)", "Banyak Produk (Excel)", "Semua Produk"], 
                                                     variable=self.mode_produk_bpb_var, command=self.update_ui_produk_bpb, width=160, corner_radius=0)
        self.dropdown_produk_bpb.grid(row=1, column=0, padx=15, pady=5)

        self.container_input_produk_bpb = ctk.CTkFrame(self.control_frame_bpb, fg_color="transparent")
        self.container_input_produk_bpb.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        self.entry_produk_bpb = ctk.CTkEntry(self.container_input_produk_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_produk_bpb.pack(side="left")

        self.mode_toko_bpb_var = ctk.StringVar(value="1 Toko (Ketik)")
        self.dropdown_toko_bpb = ctk.CTkOptionMenu(self.control_frame_bpb, values=["1 Toko (Ketik)", "Banyak Toko (Excel)", "Semua Toko"], 
                                                   variable=self.mode_toko_bpb_var, command=self.update_ui_toko_bpb, width=160, corner_radius=0)
        self.dropdown_toko_bpb.grid(row=1, column=2, padx=15, pady=5)

        self.container_input_toko_bpb = ctk.CTkFrame(self.control_frame_bpb, fg_color="transparent")
        self.container_input_toko_bpb.grid(row=1, column=3, padx=15, pady=5, sticky="w")
        self.entry_toko_bpb = ctk.CTkEntry(self.container_input_toko_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_toko_bpb.pack(side="left")

        # Baris 2: Tanggal
        ctk.CTkLabel(self.control_frame_bpb, text="TGL AWAL (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=0, padx=15, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_bpb, text="TGL AKHIR (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=1, padx=15, pady=(10, 0), sticky="w")

        self.entry_tgl_awal_bpb = ctk.CTkEntry(self.control_frame_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_awal_bpb.grid(row=3, column=0, padx=15, pady=5)
        self.entry_tgl_awal_bpb.insert(0, "2026-10-14")
        
        self.entry_tgl_akhir_bpb = ctk.CTkEntry(self.control_frame_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_akhir_bpb.grid(row=3, column=1, padx=15, pady=5)
        self.entry_tgl_akhir_bpb.insert(0, "2026-10-15")

        btn_frame_bpb = ctk.CTkFrame(self.control_frame_bpb, fg_color="transparent")
        btn_frame_bpb.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 15))

        self.btn_proses_bpb = ctk.CTkButton(btn_frame_bpb, text="↓ PROSES BPB", width=180, fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), corner_radius=0, command=self.mulai_proses_bpb)
        self.btn_proses_bpb.pack(side="left")

        self.log_area_bpb = ctk.CTkTextbox(self.frame_bpb, fg_color="#1B1410", text_color="white", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area_bpb.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)
        self.log_area_bpb.insert("0.0", "--- LOG PROSES BPB AKAN MUNCUL DI SINI ---\n\n")

    def update_ui_produk_bpb(self, pilihan):
        for widget in self.container_input_produk_bpb.winfo_children(): widget.pack_forget()
        if pilihan == "1 Produk (Ketik)":
            self.entry_produk_bpb = ctk.CTkEntry(self.container_input_produk_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_bpb.pack(side="left")
        elif pilihan == "Banyak Produk (Excel)":
            self.entry_produk_bpb = ctk.CTkEntry(self.container_input_produk_bpb, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_bpb.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_produk_bpb, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_produk_bpb)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Produk":
            self.entry_produk_bpb = ctk.CTkEntry(self.container_input_produk_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_bpb.insert(0, "(Semua Produk)")
            self.entry_produk_bpb.configure(state="disabled")
            self.entry_produk_bpb.pack(side="left")

    def update_ui_toko_bpb(self, pilihan):
        for widget in self.container_input_toko_bpb.winfo_children(): widget.pack_forget()
        if pilihan == "1 Toko (Ketik)":
            self.entry_toko_bpb = ctk.CTkEntry(self.container_input_toko_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_bpb.pack(side="left")
        elif pilihan == "Banyak Toko (Excel)":
            self.entry_toko_bpb = ctk.CTkEntry(self.container_input_toko_bpb, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_bpb.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_toko_bpb, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_toko_bpb)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Toko":
            self.entry_toko_bpb = ctk.CTkEntry(self.container_input_toko_bpb, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_bpb.insert(0, "(Semua Toko / Otomatis)")
            self.entry_toko_bpb.configure(state="disabled")
            self.entry_toko_bpb.pack(side="left")

    def catat_log_bpb(self, pesan):
        self.log_area_bpb.insert("end", pesan + "\n")
        self.log_area_bpb.see("end")

    def mulai_proses_bpb(self):
        import threading
        threading.Thread(target=self.jalankan_thread_bpb, daemon=True).start()

    def jalankan_thread_bpb(self):
        from tkinter import messagebox
        try:
            self.btn_proses_bpb.configure(state="disabled", text="MEMPROSES...")
            self.catat_log_bpb("Memulai proses BPB...")

            jalankan_proses_bpb(
                config_path=self.path_bpb,  # Menggunakan folder BPB & Retur
                output_path=self.path_output,
                mode_prod=self.mode_produk_bpb_var.get(),
                val_prod=self.entry_produk_bpb.get().strip(),
                mode_toko=self.mode_toko_bpb_var.get(),
                val_toko=self.entry_toko_bpb.get().strip(),
                tgl_awal_str=self.entry_tgl_awal_bpb.get().strip(),
                tgl_akhir_str=self.entry_tgl_akhir_bpb.get().strip(),
                callback_log=self.catat_log_bpb
            )

            messagebox.showinfo("Sukses", "Proses BPB Selesai!")
            self.tambah_riwayat_dashboard("✅ Berhasil: Ekspor data BPB selesai dilakukan.")
        except Exception as e:
            self.catat_log_bpb(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.btn_proses_bpb.configure(state="normal", text="↓ PROSES BPB")

    # ===================================================================================
    # UI MODUL RETUR
    # ===================================================================================
    def buat_halaman_retur(self):
        self.frame_retur = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=0)
        self.frame_retur.grid_rowconfigure(2, weight=1)
        self.frame_retur.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.frame_retur, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(header_frame, text="Proses Retur Toko", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2E211B").pack(side="left")
        ctk.CTkButton(header_frame, text="Engine Ready", fg_color="#4A3B32", corner_radius=0, hover=False).pack(side="right")

        self.control_frame_retur = ctk.CTkFrame(self.frame_retur, corner_radius=0, fg_color="#4A3B32")
        self.control_frame_retur.grid(row=1, column=0, sticky="ew", padx=20, pady=5)

        # Baris 1: Filter Produk dan Toko
        ctk.CTkLabel(self.control_frame_retur, text="MODE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_retur, text="INPUT / FILE PRODUK", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_retur, text="MODE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=15, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_retur, text="INPUT / FILE TOKO", text_color="white", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=15, pady=(15, 0), sticky="w")

        self.mode_produk_retur_var = ctk.StringVar(value="1 Produk (Ketik)")
        self.dropdown_produk_retur = ctk.CTkOptionMenu(self.control_frame_retur, values=["1 Produk (Ketik)", "Banyak Produk (Excel)", "Semua Produk"], 
                                                       variable=self.mode_produk_retur_var, command=self.update_ui_produk_retur, width=160, corner_radius=0)
        self.dropdown_produk_retur.grid(row=1, column=0, padx=15, pady=5)

        self.container_input_produk_retur = ctk.CTkFrame(self.control_frame_retur, fg_color="transparent")
        self.container_input_produk_retur.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        self.entry_produk_retur = ctk.CTkEntry(self.container_input_produk_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_produk_retur.pack(side="left")

        self.mode_toko_retur_var = ctk.StringVar(value="1 Toko (Ketik)")
        self.dropdown_toko_retur = ctk.CTkOptionMenu(self.control_frame_retur, values=["1 Toko (Ketik)", "Banyak Toko (Excel)", "Semua Toko"], 
                                                     variable=self.mode_toko_retur_var, command=self.update_ui_toko_retur, width=160, corner_radius=0)
        self.dropdown_toko_retur.grid(row=1, column=2, padx=15, pady=5)

        self.container_input_toko_retur = ctk.CTkFrame(self.control_frame_retur, fg_color="transparent")
        self.container_input_toko_retur.grid(row=1, column=3, padx=15, pady=5, sticky="w")
        self.entry_toko_retur = ctk.CTkEntry(self.container_input_toko_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_toko_retur.pack(side="left")

        # Baris 2: Tanggal
        ctk.CTkLabel(self.control_frame_retur, text="TGL AWAL (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=0, padx=15, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.control_frame_retur, text="TGL AKHIR (YYYY-MM-DD)", text_color="white", font=ctk.CTkFont(size=11)).grid(row=2, column=1, padx=15, pady=(10, 0), sticky="w")

        self.entry_tgl_awal_retur = ctk.CTkEntry(self.control_frame_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_awal_retur.grid(row=3, column=0, padx=15, pady=5)
        self.entry_tgl_awal_retur.insert(0, "2026-10-14")
        
        self.entry_tgl_akhir_retur = ctk.CTkEntry(self.control_frame_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
        self.entry_tgl_akhir_retur.grid(row=3, column=1, padx=15, pady=5)
        self.entry_tgl_akhir_retur.insert(0, "2026-10-15")

        btn_frame_retur = ctk.CTkFrame(self.control_frame_retur, fg_color="transparent")
        btn_frame_retur.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 15))

        self.btn_proses_retur = ctk.CTkButton(btn_frame_retur, text="↓ PROSES RETUR", width=180, fg_color="#657153", hover_color="#4E5840", text_color="white", font=ctk.CTkFont(weight="bold"), corner_radius=0, command=self.mulai_proses_retur)
        self.btn_proses_retur.pack(side="left")

        self.log_area_retur = ctk.CTkTextbox(self.frame_retur, fg_color="#1B1410", text_color="white", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area_retur.grid(row=2, column=0, sticky="nsew", padx=20, pady=15)
        self.log_area_retur.insert("0.0", "--- LOG PROSES RETUR AKAN MUNCUL DI SINI ---\n\n")

    def update_ui_produk_retur(self, pilihan):
        for widget in self.container_input_produk_retur.winfo_children(): widget.pack_forget()
        if pilihan == "1 Produk (Ketik)":
            self.entry_produk_retur = ctk.CTkEntry(self.container_input_produk_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_retur.pack(side="left")
        elif pilihan == "Banyak Produk (Excel)":
            self.entry_produk_retur = ctk.CTkEntry(self.container_input_produk_retur, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_retur.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_produk_retur, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_produk_retur)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Produk":
            self.entry_produk_retur = ctk.CTkEntry(self.container_input_produk_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_produk_retur.insert(0, "(Semua Produk)")
            self.entry_produk_retur.configure(state="disabled")
            self.entry_produk_retur.pack(side="left")

    def update_ui_toko_retur(self, pilihan):
        for widget in self.container_input_toko_retur.winfo_children(): widget.pack_forget()
        if pilihan == "1 Toko (Ketik)":
            self.entry_toko_retur = ctk.CTkEntry(self.container_input_toko_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_retur.pack(side="left")
        elif pilihan == "Banyak Toko (Excel)":
            self.entry_toko_retur = ctk.CTkEntry(self.container_input_toko_retur, width=90, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_retur.pack(side="left", padx=(0, 5))
            
            # Diubah menjadi "Pilih Excel" dan memanggil fungsi pilih_file_excel
            btn_file = ctk.CTkButton(
                self.container_input_toko_retur, 
                text="Pilih Excel", 
                width=70, 
                fg_color="#8B6D5C", 
                hover_color="#A07F6C",
                corner_radius=0, 
                command=lambda: self.pilih_file_excel(self.entry_toko_retur)
            )
            btn_file.pack(side="left")
        elif pilihan == "Semua Toko":
            self.entry_toko_retur = ctk.CTkEntry(self.container_input_toko_retur, width=160, fg_color="transparent", text_color="white", border_color="white", corner_radius=0)
            self.entry_toko_retur.insert(0, "(Semua Toko / Otomatis)")
            self.entry_toko_retur.configure(state="disabled")
            self.entry_toko_retur.pack(side="left")

    def catat_log_retur(self, pesan):
        self.log_area_retur.insert("end", pesan + "\n")
        self.log_area_retur.see("end")

    def mulai_proses_retur(self):
        import threading
        threading.Thread(target=self.jalankan_thread_retur, daemon=True).start()

    def jalankan_thread_retur(self):
        from tkinter import messagebox
        try:
            self.btn_proses_retur.configure(state="disabled", text="MEMPROSES...")
            self.catat_log_retur("Memulai proses Retur...")

            jalankan_proses_retur(
                config_path=self.path_bpb,  # Menggunakan folder BPB & Retur yang sama
                output_path=self.path_output,
                mode_prod=self.mode_produk_retur_var.get(),
                val_prod=self.entry_produk_retur.get().strip(),
                mode_toko=self.mode_toko_retur_var.get(),
                val_toko=self.entry_toko_retur.get().strip(),
                tgl_awal_str=self.entry_tgl_awal_retur.get().strip(),
                tgl_akhir_str=self.entry_tgl_akhir_retur.get().strip(),
                callback_log=self.catat_log_retur
            )

            messagebox.showinfo("Sukses", "Proses Retur Selesai!")
            self.tambah_riwayat_dashboard("✅ Berhasil: Ekspor data Retur selesai dilakukan.")
        except Exception as e:
            self.catat_log_retur(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.btn_proses_retur.configure(state="normal", text="↓ PROSES RETUR")
        
        
if __name__ == "__main__":
    app = AppHSLPR()
    app.mainloop()