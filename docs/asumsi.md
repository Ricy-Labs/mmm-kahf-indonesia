# Asumsi Simulasi Data MMM (2025)

Dokumen ini berisi parameter "kebenaran" yang ditanam ke data simulasi.
Nilai bersifat asumsi, bukan hasil pengukuran, dan bisa direvisi.

## 1. Periode dan frekuensi
- Periode: 1 Jan 2025 - 31 Des 2025
- Frekuensi: harian (365 baris)

## 2. Efek kalender terhadap penjualan dasar

| Variabel | Efek | Alasan |
|---|---|---|
| ramadan_flag | +20% | Konsumsi naik menjelang dan selama Ramadan |
| harbolnas_flag (11.11, 12.12) | +40% | Puncak promo e-commerce tahunan |
| payday_flag (tgl 25 - tgl 1) | +8% | Daya beli naik di sekitar gajian dan awal bulan |
| weekend (opsional) | +5% | Belanja online cenderung naik di akhir pekan |

## 3. Efek channel

| Channel | Adstock (half-life, hari) | Saturation | Catatan |
|---|---|---|---|
| tiktok_ads_S | 2 | Jenuh cepat | Efek cepat hilang, konten viral jangka pendek |
| instagram_ads_S | 3 | Jenuh sedang | |
| marketplace_ads_S | 2 | Jenuh sedang | Naik tajam saat Harbolnas |
| influencer_S | 7 | Jenuh sedang | Efek bertahan lebih lama, karena konten tetap terlihat |
| offline_activation_S | 10 | Jenuh lambat | Berbentuk lonjakan (event), efek tahan lebih lama |

## 4. Kontrol lain

| Variabel | Efek | Alasan |
|---|---|---|
| competitor_sales_B | Negatif kecil | Penjualan kompetitor tinggi menekan penjualan kita |
| promo_discount (kalau dipakai) | Positif | Diskon mendorong volume |

## 5. Catatan
- Data simulasi, bukan data riil perusahaan.
- Satu siklus Ramadan dan Harbolnas dalam 2025 membatasi seberapa kuat efek musiman bisa diidentifikasi model.
