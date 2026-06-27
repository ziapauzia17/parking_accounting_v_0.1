import streamlit as st
import datetime
from fpdf import FPDF

# ==========================================
# 0. INISIALISASI MEMORI (SESSION STATE)
# ==========================================
if 'jumlah_buku' not in st.session_state:
    st.session_state.jumlah_buku = 1

if 'tampil_pesan' not in st.session_state:
    st.session_state.tampil_pesan = True

# ==========================================
# 1. PENGATURAN HALAMAN & CUSTOM CSS (MOBILE SCROLL)
# ==========================================
st.set_page_config(page_title="Laporan Harian Parkir", layout="wide")

st.markdown("""
    <style>
    /* Memaksa kolom-kolom tabel buku karcis agar tetap menyamping di HP (tidak pecah ke bawah) */
    div[data-testid="stHorizontalBlock"] {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        padding-bottom: 10px;
    }
    /* Menentukan lebar minimal tiap kolom tabel agar tidak gepeng saat di-scroll di HP */
    div[data-testid="column"] {
        min-width: 140px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Pengaturan Tarif Karcis")
tarif = {
    "Motor": st.sidebar.number_input("Tarif Motor", value=5000, step=1000),
    "Mobil Pnp": st.sidebar.number_input("Tarif Mobil Penumpang", value=15000, step=5000),
    "Bus Kecil": st.sidebar.number_input("Tarif Bus Kecil", value=25000, step=5000),
    "Bus Sedang": st.sidebar.number_input("Tarif Bus Sedang", value=50000, step=10000),
    "Bus Besar": st.sidebar.number_input("Tarif Bus Besar", value=75000, step=10000)
}
kategori = list(tarif.keys())

# ==========================================
# 2. HEADER LAPORAN & BANNER NOTIFIKASI HP
# ==========================================
st.title("🅿️ Laporan Pendapatan Harian Parkir")

# Banner petunjuk untuk pengguna HP yang bisa ditutup
if st.session_state.tampil_pesan:
    with st.container():
        st.info("📱 **Saran Penggunaan:** Jika Anda mengakses aplikasi ini melalui Smartphone/HP, kami sangat menyarankan untuk menggunakan mode **Layar Miring (Landscape)** agar tabel isian nomor seri terlihat lebih luas dan rapi.")
        if st.button("✖️ Tutup Pesan Ini"):
            st.session_state.tampil_pesan = False
            st.rerun()

col1, col2, col3 = st.columns(3)
with col1:
    hari_tanggal = st.date_input("Hari / Tanggal", datetime.date.today())
    lokasi = st.selectbox("Lokasi Gerbang", ["Gate Utama", "Gate RS", "Gate Ktr", "Gate KTD", "Gate Hoba"])
with col2:
    shift = st.selectbox("Shift", ["Shift Pagi (07.00 - 19.00)", "Shift Malam (19.00 - 07.00)"])
    modal = st.number_input("Jumlah Modal (Rp)", min_value=0, value=100000, step=50000)
with col3:
    petugas = st.text_input("Nama Pengawas / Petugas")
    jml_kasir = st.selectbox("Jumlah Kasir Bertugas", [1, 2, 3, 4, 5])

# Input nama kasir secara dinamis berdasarkan jumlah kasir yang dipilih
st.markdown("**Form Nama Kasir:**")
kasir_cols = st.columns(jml_kasir)
kasir_names = []
for i in range(jml_kasir):
    nama = kasir_cols[i].text_input(f"Nama Kasir {i+1}", key=f"nama_kasir_{i}")
    kasir_names.append(nama)

st.divider()

# ==========================================
# 3. KONTROL TAMBAH / KURANG BUKU
# ==========================================
st.header("📘 Rincian Penggunaan Buku Karcis")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    if st.button("➕ Tambah Buku", use_container_width=True):
        st.session_state.jumlah_buku += 1
with col_btn2:
    if st.button("➖ Kurangi Buku", use_container_width=True):
        if st.session_state.jumlah_buku > 1:
            st.session_state.jumlah_buku -= 1
        else:
            st.warning("Minimal harus ada 1 buku karcis!")

st.markdown(f"*Total buku yang digunakan saat ini: **{st.session_state.jumlah_buku} Buku***")
st.markdown("---")

# ==========================================
# 4. BLOK PERHITUNGAN BUKU KARCIS (MATRIKS)
# ==========================================
grand_total_lembar = {k: 0 for k in kategori}
grand_total_rp = {k: 0 for k in kategori}
total_semua_uang = 0

data_buku = {}

for b in range(1, st.session_state.jumlah_buku + 1):
    st.markdown(f"### **Book {b}**")
    data_buku[b] = {'awal': {}, 'akhir': {}, 'terjual': {}, 'rupiah': {}, 'sub_tiket': 0, 'sub_rp': 0}
    
    cols = st.columns(7)
    cols[0].markdown("**Karcis**")
    for i, kat in enumerate(kategori):
        cols[i+1].markdown(f"**{kat}**")
    cols[6].markdown("**Jumlah Seluruh**")
    
    # Input nomor seri berupa text_input agar bersih dari stepper (+/-) dan mendukung angka 0 di depan
    c_awal = st.columns(7)
    c_awal[0].write("No Seri Awal")
    awal = {}
    for i, kat in enumerate(kategori):
        awal[kat] = c_awal[i+1].text_input(f"Awal {kat} b{b}", max_chars=6, key=f"aw_{b}_{kat}", label_visibility="collapsed")
        
    c_akhir = st.columns(7)
    c_akhir[0].write("No Seri Akhir")
    akhir = {}
    for i, kat in enumerate(kategori):
        akhir[kat] = c_akhir[i+1].text_input(f"Akhir {kat} b{b}", max_chars=6, key=f"ak_{b}_{kat}", label_visibility="collapsed")

    c_jual = st.columns(7)
    c_jual[0].write("**Jml Tiket Terjual**")
    
    c_rp = st.columns(7)
    c_rp[0].write("**Jumlah Rp**")
    
    subtotal_tiket = 0
    subtotal_rp = 0
    
    for i, kat in enumerate(kategori):
        val_awal = int(awal[kat]) if awal[kat].isdigit() else 0
        val_akhir = int(akhir[kat]) if akhir[kat].isdigit() else 0
        
        terjual = 0
        if val_akhir >= val_awal and val_akhir > 0:
            terjual = (val_akhir - val_awal) + 1
            
        rupiah = terjual * tarif[kat]
        
        c_jual[i+1].write(f"{terjual}")
        c_rp[i+1].write(f"{rupiah:,}")
        
        subtotal_tiket += terjual
        subtotal_rp += rupiah
        
        grand_total_lembar[kat] += terjual
        grand_total_rp[kat] += rupiah
        total_semua_uang += rupiah
        
        # Format zfill(6) untuk memastikan data yang dikirim ke fungsi PDF tetap memiliki 6 digit angka
        data_buku[b]['awal'][kat] = str(awal[kat]).zfill(6) if awal[kat] else ""
        data_buku[b]['akhir'][kat] = str(akhir[kat]).zfill(6) if akhir[kat] else ""
        data_buku[b]['terjual'][kat] = terjual
        data_buku[b]['rupiah'][kat] = rupiah

    data_buku[b]['sub_tiket'] = subtotal_tiket
    data_buku[b]['sub_rp'] = subtotal_rp

    c_jual[6].write(f"**{subtotal_tiket}**")
    c_rp[6].write(f"**{subtotal_rp:,}**")
    st.markdown("---")

# ==========================================
# 5. RANGKUMAN TOTAL SHIFT (UI LAYAR)
# ==========================================
st.header("📊 Rangkuman Total Setoran")

st.subheader("Rincian Karcis Terjual:")
col_rincian = st.columns(len(kategori))
for i, kat in enumerate(kategori):
    col_rincian[i].metric(label=f"Karcis {kat}", value=f"{grand_total_lembar[kat]} Lbr")

st.divider()

col_tot1, col_tot2, col_tot3 = st.columns(3)
col_tot1.metric("Grand Total Karcis Terjual", f"{sum(grand_total_lembar.values())} Lbr")
col_tot2.metric("Grand Total Setoran (Rp)", f"Rp {total_semua_uang:,}")
col_tot3.metric("Total Uang di Kasir (+Modal)", f"Rp {(total_semua_uang + modal):,}")

# ==========================================
# 6. FUNGSI PEMBUATAN PDF TABULAR DINAMIS
# ==========================================
def buat_pdf():
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # KOP LAPORAN
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, txt="LAPORAN HARIAN PARKING ACCOUNTING", ln=True, align='C')
    pdf.ln(5)
    
    # METADATA LAPORAN
    pdf.set_font("Arial", size=10)
    pdf.cell(30, 6, "Hari / Tanggal", 0, 0)
    pdf.cell(80, 6, f": {hari_tanggal}", 0, 0)
    pdf.cell(30, 6, "Jumlah Modal", 0, 0)
    pdf.cell(0, 6, f": Rp {modal:,}", 0, 1)
    
    pdf.cell(30, 6, "Lokasi", 0, 0)
    pdf.cell(80, 6, f": {lokasi}", 0, 0)
    
    # Gabungkan nama-nama kasir yang diisi untuk bagian metadata atas
    kasir_aktif = [n for n in kasir_names if n.strip()]
    kasir_gabungan = ", ".join(kasir_aktif) if kasir_aktif else "(Terlampir di bawah)"
    
    pdf.cell(30, 6, "Kasir", 0, 0)
    pdf.cell(0, 6, f": {kasir_gabungan}", 0, 1)
    
    pdf.cell(30, 6, "Shift", 0, 0)
    pdf.cell(80, 6, f": {shift}", 0, 0)
    pdf.cell(30, 6, "Pengawas", 0, 0)
    pdf.cell(0, 6, f": {petugas}", 0, 1)
    
    pdf.ln(8)
    
    # STRUKTUR TABEL (Mengikuti format rancangan Excel)
    col_widths = [35, 30, 35, 30, 35, 35, 40]
    headers = ["Karcis"] + kategori + ["Jumlah Seluruh"]
    
    for b in range(1, st.session_state.jumlah_buku + 1):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, f"Book {b}", 0, 1)
        
        # Cetak Baris Header Tabel
        pdf.set_font("Arial", 'B', 9)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 7, h, border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Arial", '', 9)
        # Cetak Baris No Seri Awal
        pdf.cell(col_widths[0], 6, "No Seri Awal", border=1)
        for i, kat in enumerate(kategori):
            pdf.cell(col_widths[i+1], 6, data_buku[b]['awal'][kat], border=1, align='C')
        pdf.cell(col_widths[6], 6, "-", border=1, align='C')
        pdf.ln()
        
        # Cetak Baris No Seri Akhir
        pdf.cell(col_widths[0], 6, "No Seri Akhir", border=1)
        for i, kat in enumerate(kategori):
            pdf.cell(col_widths[i+1], 6, data_buku[b]['akhir'][kat], border=1, align='C')
        pdf.cell(col_widths[6], 6, "-", border=1, align='C')
        pdf.ln()
        
        # Cetak Baris Jumlah Tiket Terjual
        pdf.cell(col_widths[0], 6, "Jml Tiket Terjual", border=1)
        for i, kat in enumerate(kategori):
            val_terjual = str(data_buku[b]['terjual'][kat]) if data_buku[b]['terjual'][kat] > 0 else ""
            pdf.cell(col_widths[i+1], 6, val_terjual, border=1, align='C')
        pdf.cell(col_widths[6], 6, str(data_buku[b]['sub_tiket']), border=1, align='C')
        pdf.ln()
        
        # Cetak Baris Jumlah Rupiah
        pdf.cell(col_widths[0], 6, "Jumlah Rp", border=1)
        for i, kat in enumerate(kategori):
            val_rp = f"{data_buku[b]['rupiah'][kat]:,}" if data_buku[b]['rupiah'][kat] > 0 else ""
            pdf.cell(col_widths[i+1], 6, val_rp, border=1, align='R')
        pdf.cell(col_widths[6], 6, f"{data_buku[b]['sub_rp']:,}", border=1, align='R')
        pdf.ln(10)
    
    # RINCIAN TOTAL LEMBAR PER JENIS KENDARAAN DI PDF
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, txt="RINCIAN LEMBAR TIKET TERJUAL:", ln=True)
    pdf.set_font("Arial", '', 10)
    for kat in kategori:
        if grand_total_lembar[kat] > 0:
            pdf.cell(50, 6, txt=f"- Karcis {kat}", ln=False)
            pdf.cell(0, 6, txt=f": {grand_total_lembar[kat]} Lembar", ln=True)
    
    pdf.ln(5)

    # TOTAL KESELURUHAN DI REKAPAN BAWAH PDF
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 8, txt=f"GRAND TOTAL KARCIS TERJUAL: {sum(grand_total_lembar.values())} Lbr", ln=False)
    pdf.cell(0, 8, txt=f"GRAND TOTAL SETORAN: Rp {total_semua_uang:,}", ln=True)
    pdf.cell(140, 8, txt=f"UANG MODAL AWAL: Rp {modal:,}", ln=False)
    pdf.cell(0, 8, txt=f"TOTAL KASIR: Rp {(total_semua_uang + modal):,}", ln=True)
    
    pdf.ln(15)
    
    # AREA TANDA TANGAN DINAMIS SISI BAWAH
    titles_ttd = [f"Kasir {i+1}" for i in range(jml_kasir)] + ["Pengawas / Petugas"]
    names_ttd = [nama if nama.strip() else "( ........................ )" for nama in kasir_names]
    names_ttd.append(petugas if petugas.strip() else "( ........................ )")
    
    # Membagi rata ruang kertas horizontal (270mm) dengan total personel yang ttd
    lebar_kolom = 270 / len(titles_ttd)
    
    # Baris Jabatan
    pdf.set_font("Arial", size=10)
    for t in titles_ttd:
        pdf.cell(lebar_kolom, 6, txt=t, align='C')
    pdf.ln(25) 
    
    # Baris Nama Terang (Bergaris Bawah)
    pdf.set_font("Arial", 'U', 10)
    for n in names_ttd:
        pdf.cell(lebar_kolom, 6, txt=n, align='C')
        
    return pdf.output(dest='S').encode('latin-1')

# Tombol Download Dokumen Resmi
st.info("💡 PDF dicetak mengikuti seluruh akumulasi buku, rincian jenis tiket, dan form tanda tangan dinamis.")
if st.download_button(
    label="📄 Simpan & Unduh Laporan PDF",
    data=buat_pdf(),
    file_name=f"Laporan_Parkir_{hari_tanggal}.pdf",
    mime="application/pdf"
):
    st.success("Laporan berhasil disimpan dan diunduh!")