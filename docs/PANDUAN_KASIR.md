# PANDUAN OPERASIONAL KASIR & RESEPSIONIS
## Sistem Manajemen Flex Gym Bitung

Dokumen ini adalah panduan praktis langkah demi langkah untuk staf kasir dan pemilik gym dalam menjalankan operasional harian.

---

### 1. Masuk ke Sistem (Login)
1. Buka browser (Google Chrome / Microsoft Edge) di komputer atau laptop kasir.
2. Buka alamat sistem gym (misal: `http://127.0.0.1:8000/` atau alamat server gym).
3. Masukkan **Username** dan **Kata Sandi** akun staf Anda.
4. Klik **Masuk ke Sistem**.

---

### 2. SOP 1: Mendaftarkan Member Baru (< 2 Menit)
Gunakan alur ini saat ada calon member yang datang ke meja resepsionis untuk mendaftar:
1. Di navbar atas, klik menu **Member**, lalu klik tombol biru **Daftar Member Baru** (atau dari dashboard klik tombol *Member Baru*).
2. Isi formulir sederhana:
   - **Nama Lengkap Member:** Ketik nama lengkap (contoh: *Michael Rumagit*).
   - **Nomor WhatsApp:** Ketik nomor HP (contoh: *081234567890*). Sistem otomatis merapikannya.
   - **Kode Member:** **Biarkan kosong** (sistem otomatis membuatkan kode unik seperti `FLX-1025`). Jika member membawa kartu berbarcode fisik dari gym, Anda boleh mengetik/menembak kode kartu tersebut.
   - **Tanggal Bergabung:** Otomatis terisi hari ini.
   - **Catatan:** Opsional (misal: *Teman Kak Budi / Ada keluhan cedera lutut*).
3. Klik **Simpan Data Member**.
4. Halaman akan langsung membuka profil member baru tersebut.
5. Klik tombol **Perpanjang / Beli Paket** untuk langsung mengaktifkan paket pertama dan mencatat pembayarannya.

---

### 3. SOP 2: Check-in Kehadiran Harian & Alat Scanner USB
Gunakan alur ini setiap kali member datang untuk berolahraga:
1. Di navbar atas, klik menu **Check-in**.
2. Kolom input kode sudah otomatis aktif (*autofocus*).
3. **Jika memakai Scanner Barcode/QR USB:** Arahkan pemindai ke kode member di kartu fisik atau HP member. Alat scanner akan otomatis mengetik kode dan menekan *Enter*.
4. **Jika mengetik manual:** Ketik kode member (misal: `FLX-1001`), lalu tekan tombol **Enter** di keyboard.
5. **Perhatikan Layar:**
   - 🟢 **LAYAR HIJAU (Check-in Berhasil):** Member berstatus aktif. Persilakan member masuk latihan.
   - 🔴 **LAYAR MERAH (Peringatan Kedaluwarsa):** Masa aktif member telah habis atau belum memiliki paket. Sampaikan secara sopan kepada member, lalu klik tombol kuning **"Perpanjang / Tagih Pembayaran Sekarang"** di layar untuk langsung memproses pembayaran.
   - ⚫ **LAYAR ABU-ABU (Kode Tidak Ditemukan):** Periksa kembali apakah ada salah ketik kode.

---

### 4. SOP 3: Perpanjangan Paket & Cetak/Kirim Struk WhatsApp
Gunakan alur ini saat member membayar iuran:
1. Dari halaman Check-in (klik tombol kuning peringatan), atau dari menu **Member** (klik tombol hijau *Paket* pada nama member).
2. **Pilih Paket:** Pilih paket keanggotaan (misal: *Paket Bulanan Regular*). Nominal pembayaran akan otomatis terisi (misal: Rp300.000).
3. **Pilih Metode Pembayaran:** Pilih *Tunai*, *Transfer Bank*, atau *QRIS Kasir*.
4. **Sistem Perpanjangan Cerdas:**
   - Jika member masih memiliki sisa hari aktif, tanggal baru otomatis menyambung dari sisa hari lama (hari aktif tidak hangus).
   - Jika member sudah kedaluwarsa, tanggal baru otomatis mulai dari hari ini.
5. Klik **Proses Pembayaran & Aktifkan**.
6. **Halaman Bukti Pembayaran Resmi (Struk) akan tampil:**
   - Klik **Cetak Struk** jika member meminta bukti fisik kertas.
   - Klik **Kirim Struk via WA** untuk langsung membuka WhatsApp web/aplikasi dan mengirimkan pesan rincian pembayaran ke HP member.

---

### 5. SOP 4: Mengirimkan Pengingat Perpanjangan WhatsApp
Lakukan pengecekan ini setiap pagi atau sore hari:
1. Di navbar atas, klik menu **Pengingat WA**.
2. Anda akan melihat dua daftar:
   - **Akan Segera Habis (H-7):** Member yang masa aktifnya tinggal 1–7 hari lagi.
   - **Baru Saja Kedaluwarsa:** Member yang masa aktifnya lewat dalam 30 hari terakhir.
3. Klik tombol hijau **Buka Chat WA** pada baris member.
4. WhatsApp akan otomatis terbuka dengan pesan sopan siap kirim yang menyebutkan nama member, sisa hari, dan nama Flex Gym Bitung. Anda cukup menekan tombol *Kirim* di WhatsApp.

---

### 6. SOP 5: Migrasi Data Buku Fisik (Impor CSV Sekaligus)
Gunakan fitur ini untuk memasukkan data member lama dari buku kasir kertas ke sistem:
1. Buka menu **Member**, lalu klik tombol **Impor Data CSV**.
2. Klik **Unduh Template CSV** untuk mendapatkan berkas contoh Excel.
3. Ketik data member lama ke dalam tabel Excel tersebut (Nama, No WA, Tanggal Mulai, Tanggal Berakhir, Catatan).
4. Simpan berkas sebagai `.csv`.
5. Unggah berkas tersebut pada tombol **Pilih Berkas CSV**, lalu klik **Mulai Impor Sekarang**.
6. Ratusan data lama akan langsung tersimpan rapi dalam beberapa detik.

---

### 7. SOP 6 (Khusus Pemilik Gym): Laporan Keuangan & Backup Database
Fitur ini khusus untuk akun Pemilik (*Owner*):
1. **Melihat Omzet & Pemasukan:**
   - Klik menu **Laporan Keuangan** di navbar atas.
   - Anda dapat melihat total omzet, memfilter rentang tanggal tertentu, dan melihat pembagian uang masuk (berapa tunai, berapa transfer, berapa QRIS).
2. **Mengamankan Salinan Data (Backup Database SQLite):**
   - Lakukan pencadangan berkala (misal: seminggu sekali atau sebulan sekali).
   - Klik tombol kuning **Backup DB** di navbar atas (atau di dalam halaman laporan).
   - Berkas database bertanggal (contoh: `backup_flexgym_20261104.sqlite3`) akan otomatis terunduh ke komputer/flashdisk Anda. Simpan berkas ini di tempat yang aman.

