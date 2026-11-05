# DECISIONS — Catatan Keputusan

Aturan: keputusan berstatus **FINAL** tidak boleh diubah agent tanpa persetujuan pemilik project. Usulan perubahan harus diajukan dulu, lalu dicatat di log di bagian bawah setelah disetujui.

## Keputusan final
| ID | Keputusan | Alasan |
|---|---|---|
| D-001 | Jenis produk: web app yang bisa dibuka dari HP/laptop, bukan aplikasi mobile native | Lebih cepat dan murah untuk MVP |
| D-002 | Bahasa UI: Indonesia. Kode, nama tabel/kolom, komentar: Inggris | Konsistensi |
| D-003 | Status member dihitung dari tanggal, tidak disimpan sebagai kolom | Menghindari data tidak sinkron |
| D-004 | **Satu deployment per gym.** Tidak ada multi-gym dalam satu sistem. Perbedaan antar gym (nama, logo, paket, fitur aktif) diatur lewat konfigurasi | Multi-gym menambah kompleksitas besar yang belum dibutuhkan |
| D-005 | **Stack: Django (Python), halaman server-rendered dengan template Django + Bootstrap.** HTMX boleh dipakai hanya jika benar-benar perlu. Tanpa frontend terpisah (React/Vue/Next.js), tanpa REST API terpisah, tanpa Docker di MVP | Lengkap (login, peran, migrasi, admin), sedikit kode, struktur baku, tidak overkill |
| D-006 | **Database: SQLite** untuk MVP. Boleh pindah ke PostgreSQL nanti lewat perubahan setting | Cukup untuk ratusan member, backup mudah |
| D-007 | **Hosting:** Siap jalan di server lokal (PC kasir gym) maupun di VPS Cloud ringan (seperti VPS Linux / PaaS Python) lewat konfigurasi WSGI/Gunicorn standar | Fleksibel terhadap kondisi jaringan internet gym di Bitung |
| D-008 | **Check-in member kedaluwarsa:** Ditandai sebagai peringatan (`expired_warning`) dengan banner/alert merah mencolok di layar kasir, agar kasir langsung menagih perpanjangan di tempat tanpa memblokir sistem | Praktis untuk kasir agar tidak kaku namun tetap mencegah member tidak bayar lolos |
| D-009 | **Zona waktu:** WITA (`Asia/Makassar`) — lokasi gym berada di Bitung, Sulawesi Utara | Menjamin batas pergantian hari dan masa aktif tepat pada pukul 00:00 WITA |
| D-010 | **Backup data:** Tombol 1-klik "Unduh Cadangan Database" di dashboard khusus Owner + skrip salinan file database `.sqlite3` terjadwal | Memudahkan pemilik gym non-teknis mengamankan data kapan saja ke laptop/flashdisk |
| D-011 | **Check-in awal lewat ketik/masukkan kode member.** `member_code` harus dibuat kompatibel dengan QR sejak awal (string pendek, unik, tanpa spasi) agar scan QR bisa ditambah nanti tanpa mengubah data | Sederhana sekarang, murah diperluas |
| D-012 | **Paket (Dasar/Standar/Lengkap) diatur lewat feature flag di konfigurasi, bukan branch git.** Satu kode untuk semua klien. Flag awal: `FEATURE_CHECKIN`, `FEATURE_REPORTS`, `FEATURE_WA_REMINDER`. Fitur yang dimatikan harus tersembunyi dari menu dan URL-nya menolak akses | Bug diperbaiki sekali, upgrade paket cukup menyalakan flag |
| D-013 | **Alur git:** `main` selalu stabil dan bisa dijalankan; satu branch per fitur (`feature/<nama>`) digabung ke `main` setelah diuji; rilis diberi tag (`v0.1`, `v1.0`). Tidak ada branch per klien atau per paket | Menghindari perbaikan berulang di banyak branch |
| D-014 | Pengaturan per gym (nama gym, logo, zona waktu, feature flag) disimpan di `.env` / file settings, bukan ditulis langsung di kode | Mendukung D-004 dan D-012 |
| D-015 | **Custom User Model sejak migrasi awal:** Menggunakan model turunan `AbstractUser` dengan atribut `role` (`owner`, `staff`) | Menghindari masalah refactoring besar database Django jika diubah di kemudian hari |
| D-016 | **Status Pembayaran Kasir:** Pembayaran tunai/transfer di kasir otomatis berstatus `verified` dengan `verified_by = staf yang login`, namun tetap tercatat di log audit owner | Mencegah antrean transaksi terhenti saat menunggu verifikasi manual owner |
| D-017 | **Input check-in autofocus & keyboard-scanner friendly:** Form check-in mendukung tombol `Enter` instan | Kompatibel langsung dengan barcode/QR scanner USB fisik tanpa perlu kode kamera |
| D-018 | **Sanitasi otomatis nomor WhatsApp:** Sistem otomatis menormalisasi format nomor HP menjadi format standar `628xxx` saat disimpan | Mencegah error URL `wa.me` akibat salah format tanda `+`, spasi, atau awalan `08` |
| D-019 | **Penanganan Akun Nonaktif / Diblokir:** Jika `is_active=False`, maka `is_membership_active` otomatis bernilai `False` dan status keanggotaan menjadi `inactive` ("Nonaktif / Diblokir"). Check-in ditolak tegas dengan status `BLOCKED` dan banner merah/hitam | Mencegah member bermasalah/diblokir lolos ke gym meskipun memiliki sisa hari paket |
| D-020 | **Validasi Duplikasi & Fleksibilitas Keluarga:** `member_code` adalah kunci unik mutlak (case-insensitive). Pendaftaran nama baru yang sama persis dengan member nonaktif/diblokir ditolak keras; nama yang sama dengan member aktif diberi peringatan ganda (soft warning); nomor WhatsApp sama diizinkan dengan notifikasi info untuk mendukung pendaftaran keluarga (ayah/anak/suami/istri) | Menjaga integritas data tanpa mengorbankan fleksibilitas operasional nyata kasir |

## Keputusan terbuka (isi sebelum fase yang bergantung padanya dimulai)
*(Semua keputusan utama awal telah ditetapkan dan disetujui)*

## Log perubahan keputusan
| Tanggal | ID | Perubahan | Disetujui oleh |
|---|---|---|---|
| 2026-11-04 | D-004, D-005, D-006, D-011 sampai D-014 | Ditetapkan: Django + SQLite, satu deployment per gym, feature flag, alur git, check-in via kode | Pemilik project |
| 2026-11-04 | D-007 sampai D-010, D-015 sampai D-018 | Penetapan zona waktu WITA (Bitung), perilaku check-in warning, strategi backup 1-klik, custom user model, verifikasi instan kasir, scanner autofocus, sanitasi WA | Pemilik project |
| 2026-11-05 | D-019, D-020 | Penegakan pemblokiran total check-in untuk akun nonaktif, validasi cerdas duplikasi nama/kode/HP ramah pendaftaran keluarga | Pemilik project |
