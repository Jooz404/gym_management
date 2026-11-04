# PROJECT BRIEF — Flex Gym Bitung

## 1. Latar belakang
**Flex Gym Bitung**, sebuah gym lokal di Kota Bitung, Sulawesi Utara belum memiliki website maupun pengelolaan member digital; data member dan pembayaran saat ini masih dicatat di kertas (hardcopy). Akibatnya masa aktif sulit dipantau, pencatatan pembayaran rentan selisih, dan tidak ada riwayat kehadiran member.

## 2. Tujuan
Membuat web app sederhana agar pemilik dan staf gym dapat:
1. Mengetahui siapa saja member yang aktif dan kapan masa aktifnya habis secara real-time.
2. Mencatat pembayaran dan melihat laporan pemasukan harian dan bulanan.
3. Mencatat kehadiran (check-in) dan menandai peringatan bagi member yang masa aktifnya sudah kedaluwarsa.
4. Menghubungi member yang akan habis masa aktifnya (pengingat perpanjangan via tautan WhatsApp langsung).

Tujuan jangka panjang: sistem dapat dipakai ulang untuk gym lain tanpa dibangun dari nol (cukup atur konfigurasi/feature flag per gym).

## 3. Pengguna
| Peran | Kebutuhan utama |
|---|---|
| Pemilik (owner) | Lihat laporan keuangan, member aktif/habis, kelola paket, kelola akun staf, dan unduh backup data |
| Staf/kasir (staff) | Daftarkan member baru, catat pembayaran perpanjangan, proses check-in member |
| Member | Tidak punya login di MVP (hanya punya kode/QR member fisik/digital di HP) |

## 4. Fakta gym target
- **Lokasi gym:** Kota Bitung, Sulawesi Utara (Zona Waktu: WITA / `Asia/Makassar`).
- **Iuran member:** Rp300.000 per bulan (standar, dapat disesuaikan).
- **Jenis paket:** Bulanan (30 hari), Harian (1 hari), dan fleksibel sesuai kebutuhan pengelola.
- **Metode pembayaran:** Tunai (cash), Transfer bank, QRIS statis kasir.
- **Perangkat operasional:** PC Desktop / Laptop di meja kasir/resepsionis gym, antarmuka responsif untuk HP/tablet.
- **Koneksi internet:** Dirancang efisien untuk koneksi lokal gym maupun hosting cloud.
- **Dukungan hardware tambahan:** Kompatibel dengan Barcode/QR Scanner USB fisik (plug-and-play).

## 5. Scope MVP (yang DIKERJAKAN)
1. **Login staf/owner** dengan dua peran (Custom User model Django).
2. **Data member:** tambah, ubah, cari (nama/kode), lihat riwayat kehadiran & membership. Format WA otomatis ternormalisasi.
3. **Paket keanggotaan:** nama, durasi (hari), harga; dapat diaktifkan/dinonaktifkan.
4. **Keanggotaan (masa aktif):** mulai, berakhir, status aktif/habis dihitung dinamis; perpanjangan menjaga sisa hari aktif.
5. **Pembayaran:** catat nominal, metode, tanggal; default status terverifikasi langsung untuk transaksi kasir.
6. **Check-in cepat:** lewat ketik kode member atau scan alat scanner USB (autofocus); sistem menandai peringatan bagi member kedaluwarsa.
7. **Dashboard sederhana:** jumlah member aktif, yang akan habis 7 hari ke depan, yang sudah habis, pemasukan hari ini dan bulan ini.
8. **Pengingat perpanjangan:** daftar member akan habis dengan tombol buka WhatsApp (`wa.me`) pesan template siap kirim.
9. **Cadangan data:** tombol 1-klik unduh backup file database SQLite di halaman Owner.
10. **Impor data awal:** fasilitas impor dari template file CSV data kertas lama.

## 6. Di luar scope (TIDAK dikerjakan di MVP)
- Aplikasi mobile native dan portal login member
- Pembayaran online otomatis / payment gateway pihak ketiga
- Bot pengingat WhatsApp otomatis (gateway API berbayar)
- Booking kelas dan personal trainer
- Multi-cabang / multi-tenant dalam satu basis data tunggal (cukup satu deployment per gym)
- Website promosi gym (dikerjakan terpisah)
- Integrasi pintu akses fisik (turnstile / palang otomatis)

## 7. Kriteria berhasil MVP
- Staf bisa mendaftarkan member baru + mencatat pembayaran awal dalam kurang dari 2 menit.
- Pemilik bisa melihat daftar member yang akan habis dalam 1 klik.
- Check-in member kedaluwarsa tampil jelas sebagai peringatan mencolok untuk penagihan di tempat.
- Data lama dari catatan kertas berhasil diimpor melalui file CSV.
- Dipakai sungguhan oleh gym selama masa uji coba 2–4 minggu tanpa kehilangan data.

## 8. Asumsi dan risiko
- Staf kasir mungkin belum terbiasa dengan sistem komputer, sehingga alur UI dibuat sangat ringkas dan to-the-point.
- Migrasi data dari kertas difasilitasi dengan template Excel/CSV yang mudah dipahami.
