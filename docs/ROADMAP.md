# ROADMAP

Aturan: satu fase selesai dan diuji, baru lanjut. Setiap fase punya "Selesai jika" yang harus terpenuhi.

## Fase 0 — Persiapan (sebelum coding)
- [x] `PROJECT_BRIEF.md`: semua parameter utama dan konteks gym (Flex Gym Bitung, Sulut) terisi
- [x] `DECISIONS.md`: semua keputusan terbuka (D-007 s/d D-010) & penambahan D-015 s/d D-018 disetujui
- [x] Pemahaman ringkasan agent telah disetujui oleh pemilik proyek
- [x] Repositori git dibuat, branch `main` dan aturan alur kerja D-013 berlaku
- [x] Template impor CSV catatan kertas disiapkan (`docs/template_import_member.csv`)
- [x] Environment Python (virtual environment, Django 5.1, python-dotenv) terpasang
**Selesai jika:** repositori git aktif, env siap, struktur dasar siap tanpa konflik konfigurasi. (SELESAI)

## Fase 1 — Fondasi
Project Django, konfigurasi `.env` (+ `.env.example`), Custom User model (`AbstractUser` dengan role `owner` & `staff`), zona waktu WITA (`Asia/Makassar`), SQLite + migrasi awal, login dua peran, kerangka feature flag (`FEATURE_CHECKIN`, `FEATURE_REPORTS`, `FEATURE_WA_REMINDER`) dan pengaturan per gym (D-014), layout dasar responsif dengan Bootstrap 5.
**Selesai jika:** staf dan owner bisa login, halaman terproteksi menolak yang belum login, role permission berjalan, dan mengubah flag di konfigurasi menyembunyikan/menampilkan menu terkait.

## Fase 2 — Member dan paket
CRUD member (tambah, ubah, cari nama/kode, sanitasi nomor WA otomatis D-018), CRUD paket (nama, durasi, harga, aktif/nonaktif).
**Selesai jika:** bisa menambah 20 member contoh dan mencarinya berdasarkan nama atau kode secara instan.

## Fase 3 — Keanggotaan dan pembayaran
Buat dan perpanjang membership, catat pembayaran (status terverifikasi otomatis oleh staf D-016), kalkulasi aturan masa aktif sesuai `DATA_MODEL.md` (menjaga akumulasi sisa hari aktif jika diperpanjang sebelum habis).
**Selesai jika:** unit test aturan perpanjangan lulus (skenario member aktif dan member kedaluwarsa).

## Fase 4 — Check-in Cepat
Check-in lewat kode member (D-011), input autofocus dan kompatibel keyboard/scanner USB (D-017), peringatan mencolok untuk member habis (D-008), riwayat kehadiran. Dilindungi `FEATURE_CHECKIN`.
**Selesai jika:** check-in member aktif sukses, check-in member kedaluwarsa menampilkan peringatan tagihan di kasir, dan modul terkunci jika flag mati.

## Fase 5 — Dashboard, Laporan & Fitur Khusus Owner
Ringkasan angka kartu dashboard, daftar member akan habis (7 hari) & sudah habis, tombol WhatsApp pesan siap kirim (`FEATURE_WA_REMINDER`), laporan pemasukan harian/bulanan (`FEATURE_REPORTS`), dan tombol 1-klik unduh cadangan database `.sqlite3` bagi owner (D-010).
**Selesai jika:** angka dashboard cocok dengan data riil transaksi, tombol WhatsApp membuka chat dengan format valid, dan unduhan file backup berjalan normal.

## Fase 6 — Migrasi Data & Uji Coba Lapangan
Fasilitas impor data awal dari file template CSV, pengujian skenario menyeluruh, panduan singkat untuk staf kasir di Bitung, masa uji coba gym 2–4 minggu.
**Selesai jika:** tidak ada data hilang, data awal kertas berhasil masuk, dan staf kasir dapat menjalankan alur pendaftaran dan check-in mandiri.

## Ide ditunda (jangan dikerjakan dulu di MVP)
Semua ide di bawah dikerjakan setelah MVP berjalan stabil:
| Ide | Status | Catatan |
|---|---|---|
| Website promosi gym publik | Ditunda | Dibuat terpisah dari aplikasi web manajemen |
| Pengingat WhatsApp otomatis (bot API) | Ditunda | Evaluasi pemakaian manual terlebih dahulu |
| Scan QR langsung via kamera web | Ditunda | `member_code` sudah kompatibel barcode/QR scanner USB fisik |
| Booking kelas / personal trainer | Ditunda | Butuh tabel relasi baru |
| Payment gateway otomatis (Midtrans/Xendit) | Ditunda | Pembayaran kasir tunai/transfer/QRIS statis sudah mencukupi |
| Multi-tenant database tunggal | Ditolak | Tetap 1 deployment per gym (D-004) |
