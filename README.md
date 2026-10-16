# mmm-kahf-indonesia
Marketing Mix Modeling untuk brand skincare pria (Kahf) di konteks Indonesia. Data simulasi, model Bayesian, dashboard Streamlit.



## Sumber Data & Asumsi

### Data simulasi
Proyek ini memakai **data simulasi** (periode 1 Jan - 31 Des 2025, frekuensi
harian), bukan data marketing riil, karena data spend perusahaan bersifat
rahasia. Karena itu, hasil model **tidak boleh dibaca sebagai temuan tentang
bisnis nyata**. Fungsinya untuk menunjukkan alur kerja MMM dan menguji apakah
model mampu menemukan kembali parameter yang sengaja ditanam di data.

### Flag kalender
Variabel kontrol kalender dibuat dari referensi publik:

| Variabel | Definisi | Sumber / dasar |
|---|---|---|
| `ramadan_flag` | 1 - 30 Maret 2025 | Penetapan awal Ramadan oleh Kemenag dan SKB libur nasional (Idul Fitri 31 Maret 2025) |
| `harbolnas_flag` | 10 - 16 Desember 2025 (puncak 12.12) | Jadwal resmi Harbolnas 2025 dari idEA dan Kemenkomdigi |
| `payday_flag` | Tanggal 25 sampai tanggal 1 bulan berikutnya | Keputusan tim: konsumsi cenderung naik di sekitar gajian dan awal bulan |

### Asumsi efek (parameter simulasi)
Besaran efek Ramadan, Harbolnas, dan payday, serta kecepatan adstock dan
saturasi tiap channel, adalah **asumsi tim**, bukan hasil riset atau
pengukuran. Nilainya didokumentasikan di `docs/asumsi.md` beserta alasannya,
dan dapat diubah di `src/config.py`.

## Limitasi

- **Bukan inferensi kausal.** Model mempelajari pola dari data historis, jadi
  selalu ada ketidakpastian statistik. Hasil dilaporkan sebagai rentang
  (credible interval), bukan satu angka pasti.
- **Data simulasi.** Pola yang ditemukan model mencerminkan asumsi yang kami
  tanam, bukan perilaku pasar sebenarnya.
- **Periode hanya satu tahun.** Ramadan dan Harbolnas muncul satu kali, sehingga
  efek musiman sulit dipisahkan dari tren atau efek channel yang kebetulan
  naik pada waktu yang sama.
- **Kualitas hasil bergantung pada variabel kontrol.** Faktor yang tidak
  dimasukkan ke model (misalnya [promo/diskon, kondisi ekonomi]) dapat
  menggeser kontribusi channel secara keliru.
