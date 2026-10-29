# Asumsi Simulasi Data MMM (2025)

Dokumen ini mencatat parameter "kebenaran" yang ditanam ke data simulasi.
Sumber nilai: `src/config.py` (`SIM_PARAMS`) dan `src/simulate_data.py`.
Semua nilai efek adalah **asumsi tim**, bukan hasil riset atau pengukuran, dan dapat direvisi.
Data bersifat simulasi dan tidak berasal dari atau berafiliasi dengan brand nyata mana pun.

## 1. Periode dan frekuensi

- Periode: 1 Jan 2025 - 31 Des 2025
- Frekuensi: harian (365 baris), `seed = 42`
- Kolom: `date`, `sales` (target), 5 kolom spend channel, kolom kontrol (lihat bagian 4)
- Satuan `sales` dan spend adalah unit relatif, tidak dikalibrasi ke rupiah

## 2. Struktur penjualan

```
sales = (baseline + sum(efek channel) + efek kompetitor) x pengali_musim + noise
```

| Komponen | Nilai | Catatan |
|---|---|---|
| Baseline | 400 | `base_sales` |
| Tren | +0,1 per hari | Naik linear sepanjang tahun |
| Noise | sd 20 | Acak, normal |
| Efek kompetitor | -0,1 per unit penjualan kompetitor di atas 450 | Penjualan kompetitor berupa random walk mulai dari 450 |

Pengali musim bersifat **multiplikatif** terhadap seluruh komponen di atas, termasuk efek channel.

## 3. Efek kalender (pengali musim)

`pengali_musim = 1 + 0,20 x ramadan + 0,40 x harbolnas + 0,08 x payday + 0,05 x weekend`

| Variabel | Definisi | Efek | Dasar penetapan tanggal |
|---|---|---|---|
| `ramadan_flag` | 1 - 30 Maret 2025 | +20% | Penetapan awal Ramadan oleh Kemenag; Idul Fitri 31 Maret 2025 (SKB libur nasional) |
| `harbolnas_flag` | 10 - 16 Desember 2025 (puncak 12.12) | +40% | Jadwal Harbolnas 2025 dari idEA dan Kemenkomdigi |
| `payday_flag` | Tanggal 25 s.d. tanggal 1 bulan berikutnya | +8% | Keputusan tim: konsumsi cenderung naik di sekitar gajian dan awal bulan |
| `weekend_flag` | Sabtu dan Minggu | +5% | Belanja online cenderung naik di akhir pekan |

Catatan:
- Seluruh 7 hari Harbolnas memakai efek yang sama (+40%); tidak ada pembedaan hari puncak.
- Lebaran tidak dimodelkan terpisah; dianggap tercakup di `ramadan_flag`.
- `promo_discount` **tidak dipakai** dalam simulasi ini.

## 4. Variabel kontrol di data

`ramadan_flag`, `harbolnas_flag`, `payday_flag`, `weekend_flag`, `competitor_sales_B`
(sesuai `CONTROL_COLS` di `src/config.py`).

## 5. Efek channel

Pola spend harian dasar: `mean x Gamma(4; 0,25)`. Pada Ramadan dan Harbolnas, spend semua channel dinaikkan 20% (`boost`).
Adstock geometrik dengan `l_max = 28`; decay harian = 0,5^(1/half-life).
Saturasi memakai kurva Hill: `x / (x + k)`, dengan `k = pengali x rata-rata adstock`
(pengali: cepat 0,5; sedang 1,0; lambat 2,0).
Efek channel = `beta x saturasi(adstock(spend))`.

| Channel | Mean spend | Half-life (hari) | Decay harian | Saturasi | Beta | Pola spend |
|---|---|---|---|---|---|---|
| `tiktok_ads_S` | 15 | 2 | 0,71 | Cepat | 100 | Fluktuatif harian |
| `instagram_ads_S` | 25 | 3 | 0,79 | Sedang | 120 | Fluktuatif harian |
| `marketplace_ads_S` | 30 | 2 | 0,71 | Sedang | 150 | Fluktuatif; spend x3 saat Harbolnas |
| `influencer_S` | 40 | 7 | 0,91 | Sedang | 180 | Fluktuatif harian |
| `offline_activation_S` | 8 | 10 | 0,93 | Lambat | 60 | Lonjakan event: sekitar 4% hari, sisanya nol |

## 6. Jawaban benar untuk validasi model

Hasil perhitungan dari simulasi (`data/processed/true_contributions.csv`).
`share benar` = kontribusi channel (sudah dikalikan pengali musim) dibagi total penjualan.

| Channel | Share benar | Share tanpa pengali musim | Porsi spend | Penjualan per unit spend* |
|---|---|---|---|---|
| `influencer_S` | 12,4% | 11,6% | 36,4% | 2,2 |
| `instagram_ads_S` | 8,2% | 7,8% | 21,7% | 2,5 |
| `marketplace_ads_S` | 10,2% | 9,6% | 26,2% | 2,6 |
| `tiktok_ads_S` | 9,2% | 8,6% | 13,1% | 4,6 |
| `offline_activation_S` | 1,9% | 1,8% | 2,5% | 5,1 |
| **Total media** | **41,9%** | **39,4%** | 100% | |

*Kasar: kontribusi (share benar x total penjualan) dibagi total spend channel; bukan ROI inkremental murni.

Urutan share benar: influencer > marketplace > TikTok > Instagram > offline.
Urutan penjualan per unit spend: offline > TikTok > marketplace > Instagram > influencer.

Dua versi jawaban benar disediakan karena model aditif tidak dapat menangkap pengali musim:
bandingkan model aditif dengan kolom "tanpa pengali musim", dan model yang menangani interaksi musim dengan kolom "share benar".

## 7. Catatan untuk validasi

- Simulasi memakai kurva saturasi Hill, sedangkan model memakai `LogisticSaturation`; bentuk kurvanya berbeda sehingga parameter tidak akan identik.
- Simulasi memiliki tren linear; model awal tidak memiliki komponen tren.
- Spend semua channel naik saat Ramadan dan Harbolnas, dan spend marketplace melonjak tajam saat Harbolnas. Ini membuat spend berkorelasi dengan flag musim dan menyulitkan pemisahan efek.
- Satu siklus Ramadan dan Harbolnas dalam 2025 membatasi seberapa kuat efek musiman dapat diidentifikasi.

## 8. Limitasi

- Data simulasi, bukan data riil perusahaan; hasil model tidak boleh dibaca sebagai temuan tentang bisnis nyata.
- Seluruh angka efek, adstock, saturasi, dan baseline adalah asumsi tim.
- Tanggal Ramadan, Idul Fitri, dan Harbolnas bersumber dari referensi publik (Kemenag, SKB libur nasional, idEA, Kemenkomdigi); aturan `payday_flag` adalah keputusan tim.
