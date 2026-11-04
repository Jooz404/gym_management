# AGENTS.md — Aturan Kerja untuk AI Agent

Project: **gym_management** — sistem manajemen member gym (web app) untuk gym kecil yang saat ini masih mencatat manual.

## 1. Wajib dibaca sebelum mengerjakan apa pun
Baca berurutan, lalu ringkas pemahamanmu dalam 5-8 kalimat dan tunggu konfirmasi saya:
1. `docs/PROJECT_BRIEF.md` — tujuan, scope MVP, dan hal yang TIDAK dikerjakan
2. `docs/DECISIONS.md` — keputusan yang sudah final (stack, aturan bisnis)
3. `docs/DATA_MODEL.md` — struktur data
4. `docs/ROADMAP.md` — fase kerja dan "definition of done"

Jika ada konflik antar dokumen, `DECISIONS.md` menang. Jika dokumen belum menjawab sesuatu, **tanya saya, jangan menebak**.

## 2. Aturan main
- **Jangan menambah fitur di luar scope MVP** di `PROJECT_BRIEF.md`. Ada ide bagus? Catat di bagian "Ide Ditunda" di `ROADMAP.md`, jangan dikerjakan.
- **Kerjakan per fase dan per langkah kecil.** Satu tugas selesai, bisa dijalankan, baru lanjut. Jangan membangun banyak modul sekaligus.
- **Sebelum menulis kode untuk fase baru**, tulis rencana singkat (file yang akan dibuat/diubah, alasan) dan tunggu persetujuan saya.
- **Jangan mengubah stack, struktur database, atau aturan bisnis secara diam-diam.** Perubahan harus diusulkan dulu, lalu dicatat di `DECISIONS.md` setelah saya setuju.
- **Jangan menghapus atau menimpa data/file** tanpa konfirmasi.
- Setelah tiap tugas selesai: jelaskan apa yang berubah, cara menjalankannya, dan cara mengujinya.
- Jika menemukan bug atau masalah di luar tugas, laporkan, jangan langsung diperbaiki.

## 3. Standar kode
- Identifier, nama tabel/kolom, dan komentar kode: **bahasa Inggris**.
- Teks yang tampil ke pengguna (UI, pesan error): **bahasa Indonesia**.
- Komunikasi denganku: **bahasa Indonesia**.
- Rahasia (password, token, API key) hanya lewat file `.env`, tidak boleh ditulis di kode atau di-commit. Sediakan `.env.example`.
- Password disimpan sebagai hash. Validasi semua input di sisi server.
- Tanggal disimpan konsisten (zona waktu ditentukan di `DECISIONS.md`).
- Tambahkan tes untuk aturan bisnis penting (hitung masa aktif, status kedaluwarsa, check-in ditolak).

## 4. Stack dan alur kerja (ringkasan, rujukan utama tetap `DECISIONS.md`)
- Django + SQLite, template server-rendered + Bootstrap. **Jangan** menambah React/Vue, REST API terpisah, Docker, atau dependency besar tanpa persetujuan.
- Satu deployment per gym; pengaturan per gym lewat konfigurasi (D-004, D-014).
- Paket Dasar/Standar/Lengkap = **feature flag**, bukan branch (D-012). Setiap fitur opsional wajib patuh pada flag-nya: menu tersembunyi dan URL menolak akses saat flag mati.
- Git: `main` selalu stabil; satu branch per fitur `feature/<nama>`; jangan commit langsung ke `main`; jangan membuat branch per klien (D-013).

## 5. Konteks bisnis singkat
Pemilik gym bukan orang teknis. Kesederhanaan lebih penting daripada kelengkapan. Setiap layar harus bisa dipakai staf yang tidak terbiasa dengan aplikasi. Jika ragu antara "lengkap" dan "sederhana", pilih sederhana.
