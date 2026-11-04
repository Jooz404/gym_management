# DATA MODEL

> Rancangan data model telah disesuaikan dengan kesepakatan `DECISIONS.md`.

## Tabel

**users** (staf dan owner)
- Menggunakan Custom User Model Django (`AbstractUser`) (D-015).
- Field: `id`, `name`, `username` (unik), `password_hash`, `role` (`owner` | `staff`), `is_active`, `created_at`.

**members**
- Field: `id`, `member_code` (unik, string pendek huruf/angka tanpa spasi, kompatibel QR/barcode D-011), `full_name`, `phone_wa` (sanitasi otomatis format `628xxx` D-018), `join_date`, `notes`, `is_active`, `created_at`.

**packages**
- Field: `id`, `name`, `duration_days`, `price`, `is_active`.
- Contoh: Paket Bulanan (30 hari, Rp300.000), Paket Harian (1 hari), Paket Tahunan (365 hari).

**memberships** (periode masa aktif seorang member)
- Field: `id`, `member_id`, `package_id`, `start_date`, `end_date`, `created_by`, `created_at`.

**payments**
- Field: `id`, `membership_id`, `amount`, `method` (`cash` | `transfer` | `qris`), `paid_at`, `status` (`pending` | `verified` — default `verified` untuk transaksi kasir di tempat D-016), `verified_by`, `proof_path` (opsional), `note`, `created_by`.

**checkins**
- Field: `id`, `member_id`, `checked_in_at`, `method` (`code` | `qr` | `manual`), `result` (`allowed` | `expired_warning`), `recorded_by`.
- Form check-in autofocus dan siap menerima input scanner USB fisik (D-017).

## Relasi
- 1 member punya banyak memberships
- 1 membership punya 1 atau lebih payments
- 1 member punya banyak checkins

## Aturan turunan (jangan disimpan sebagai kolom terpisah, hitung dari data)
- **Status member:** aktif jika ada membership dengan `end_date >= hari ini` (zona waktu WITA D-009); selain itu habis/kedaluwarsa.
- **end_date** = start_date + duration_days dari paket.
- **Perpanjangan:** jika member masih aktif, membership baru dimulai dari `end_date` lama + 1 hari (masa sisa tidak hilang). Jika sudah habis, mulai dari tanggal perpanjangan.
- **Akan habis:** `end_date` dalam 7 hari ke depan.
- **Check-in** member habis: tetap dicatat dengan `result = expired_warning`, dan memunculkan peringatan merah di UI kasir untuk ditagih di tempat (D-008).

## Keputusan terkait
- Tidak ada kolom `gym_id`: satu deployment per gym (DECISIONS D-004).
- Database SQLite (D-006); model ditulis sebagai Django models dan migrasi.
- Tombol backup 1-klik di dashboard owner untuk unduh file `.sqlite3` (D-010).
- `member_code`: string pendek, unik, tanpa spasi, kompatibel QR (D-011).
- Paket harian: tetap lewat `packages` dengan `duration_days = 1`.
