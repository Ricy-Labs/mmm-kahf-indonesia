# Error Analysis Model MMM (Minggu 6)

Dokumen ini membandingkan estimasi model dengan jawaban benar yang ditanam di data simulasi,
lalu menjelaskan channel mana yang meleset dan kenapa.

- Model yang dianalisis: **multiplikatif + komponen tren, `target_accept = 0.97`**
  (`results/channel_results_multiplicative_trend_ta97.csv`). Ini satu-satunya fit dengan
  diagnostik sehat (0 divergences, r_hat 1,005, ESS minimum 515).
- Catatan: `data/processed/model_results.csv` berisi fit **tanpa tren**, jadi angkanya berbeda
  dari tabel di bawah.
- Interval kredibel: HDI 94%.
- Semua hipotesis di bawah adalah **dugaan dari hasil dan perhitungan di data simulasi**, kecuali
  yang ditandai sudah diuji.

## 1. Ringkasan hasil

| Channel | Share benar | Share estimasi (HDI 94%) | Selisih | Benar di dalam HDI? |
|---|---|---|---|---|
| `influencer_S` | 12,4% | 8,4% (2,3 - 16,1) | -4,0 | Ya |
| `instagram_ads_S` | 8,2% | 2,7% (0,03 - 6,1) | -5,5 | **Tidak** |
| `marketplace_ads_S` | 10,2% | 11,0% (4,8 - 18,5) | +0,7 | Ya |
| `tiktok_ads_S` | 9,2% | 8,8% (0,03 - 22,0) | -0,3 | Ya (interval sangat lebar) |
| `offline_activation_S` | 1,9% | 1,0% (0,4 - 1,5) | -1,0 | **Tidak** (tipis) |
| **Total media** | **41,9%** (39,5% tanpa pengali musim) | **31,9%** | **-10,1** (-7,7) | |

| Channel | ROI benar* | ROI estimasi (HDI 94%) | Benar di dalam HDI? |
|---|---|---|---|
| `influencer_S` | 2,2 | 1,5 (0,4 - 2,9) | Ya |
| `instagram_ads_S` | 2,5 | 0,8 (0,01 - 1,8) | **Tidak** |
| `marketplace_ads_S` | 2,6 | 2,7 (1,2 - 4,6) | Ya |
| `tiktok_ads_S` | 4,6 | 4,4 (0,02 - 11,0) | Ya (interval sangat lebar) |
| `offline_activation_S` | 5,1 | 2,6 (1,0 - 4,0) | **Tidak** |

*Kontribusi channel dibagi total spend channel (kasar, bukan ROI inkremental murni).

Status kriteria lanjut ke dashboard: K1 (diagnostik) lolos, K4 (urutan ROI ekstrem) lolos,
K2 (jawaban benar masuk HDI untuk minimal 4 dari 5 channel) belum (3 dari 5),
K3 (total share dalam ±5 poin) belum.

## 2. Hal pertama yang perlu dilihat: gap total ±10 poin dari mana?

Dari -10,1 poin total, **hampir seluruhnya berasal dari dua channel**:
Instagram (-5,5) dan influencer (-4,0), atau sekitar 94% dari gap.
Marketplace dan TikTok sudah hampir tepat, dan offline hanya -1,0.

Jadi pertanyaan utamanya bukan "kenapa semua channel meleset", tapi
**"kenapa Instagram dan influencer terbaca terlalu kecil"**.

## 3. Analisis per channel

### Instagram (meleset terbesar, di luar HDI)

- Estimasi share 2,7% vs benar 8,2%; ROI 0,8 vs benar 2,5.
- Posterior sangat lebar (HDI share mulai hampir 0) dan adstock sulit diidentifikasi.
- **Dugaan penyebab:** efek Instagram hampir konstan sepanjang tahun. Dari perhitungan di data
  simulasi, efek harian channel ini hanya bervariasi ±11% dari rata-ratanya (CV 0,11), dan variasi
  yang tersisa setelah efek tren, musiman, dan flag kalender dibuang hanya sekitar 5,5 unit,
  jauh di bawah noise acak (sd 20). Efek yang nyaris rata seperti ini sulit dibedakan dari
  intercept, sehingga sebagian terserap ke baseline.
- **Dampak bisnis:** model akan menyarankan "kurangi Instagram" padahal di simulasi ROI-nya
  justru di atas rata-rata. Rekomendasi seperti itu tidak boleh dipakai dari model ini.

### Influencer (di bawah, tapi masih di dalam HDI)

- Estimasi share 8,4% vs benar 12,4%; ROI 1,5 vs benar 2,2.
- Adstock terbaca benar (0,92 vs benar 0,91), tapi besar efek (`beta`) tidak pasti.
- **Dugaan penyebab:** half-life panjang (7 hari) membuat efeknya mulus, dan sekitar 50% dari
  variasinya bisa dijelaskan oleh tren, musiman, dan flag kalender. Variasi yang benar-benar khas
  channel ini hanya sekitar 7,5 unit. Selisihnya ikut terserap intercept dan komponen tren.

### Marketplace (sekarang hampir tepat)

- Share 11,0% vs 10,2%. Tanpa tren, estimasinya 14,4% (kelebihan +4,2 poin).
- **Hipotesis yang sudah teruji:** menambah komponen tren menurunkan kelebihan ini. Sebelumnya
  kenaikan penjualan sepanjang tahun, serta lonjakan spend saat Harbolnas, ikut dikreditkan ke
  marketplace. Setelah ada tren, dan Harbolnas ditangani flag, kelebihan itu hampir hilang.
- Sisa risiko: spend marketplace tetap berkorelasi dengan Harbolnas (±0,43), jadi interval masih
  cukup lebar (4,8% - 18,5%).

### TikTok (tepat di rata-rata, interval sangat lebar)

- Share 8,8% vs 9,2% (tanpa tren 6,1%, jadi tren memperbaiki -3,1 poin).
- **Hati-hati membaca "tepat":** HDI share 0,03% - 22,0% dan ROI 0,02 - 11,0. Hasilnya tidak salah,
  tapi juga **tidak informatif**. Model belum mampu memberi kepastian untuk channel ini.

### Offline activation (meleset tipis, terlalu yakin)

- Share 1,0% vs 1,9%; ROI 2,6 vs benar 5,1.
- Hanya ada sekitar 12 hari event dalam setahun, sehingga datanya sangat sedikit.
- Intervalnya sempit (0,4% - 1,5%) tapi meleset tipis di bawah jawaban benar. Itu tanda model
  **terlalu yakin**, bukan sekadar tidak pasti.
- Kontribusi benarnya kecil (1,9%), jadi selisih -1,0 poin tidak banyak mengubah total.

## 4. Status hipotesis penyebab

| Hipotesis | Status | Bukti |
|---|---|---|
| H1. Model tanpa tren menyerap kenaikan penjualan ke channel | **Didukung** | MAE share turun 3,8 ke 2,3 poin; marketplace +4,2 ke +0,7; TikTok -3,1 ke -0,3 |
| H2. Struktur aditif vs multiplikatif menyebabkan gap total | **Ditolak** | Gap ±10 poin muncul juga di data aditif; pengali musim hanya menggeser total sekitar 2-3 poin |
| H3. Efek channel yang rata (always-on) terserap intercept | **Konsisten, belum diuji** | Intercept model ±64% dari sales vs baseline benar ±55%; efek Instagram dan influencer variasinya kecil |
| H4. Instagram dan offline sulit diidentifikasi (data sedikit) | **Didukung** | Posterior lebar (Instagram), hanya ±12 hari event (offline), interval offline meleset |
| H5. Bentuk saturasi berbeda (Hill di simulasi vs Logistic di model) | **Belum diuji** | Saturasi Hill dicoba sekali dan tidak konvergen (r_hat 1,18, ESS 9) |

## 5. Apa artinya untuk proyek

1. **Model sehat secara statistik tapi belum bisa dipercaya untuk keputusan antar-channel.**
   Hanya satu kesimpulan yang cukup kuat: ROI marketplace di atas 1 (HDI 1,2 - 4,6).
   Untuk influencer, Instagram, dan TikTok, interval terlalu lebar atau meleset untuk menentukan
   peringkat atau realokasi budget.
2. **Sumber masalah kemungkinan besar sifat data, bukan bug kode.** Channel yang berjalan konstan
   sepanjang tahun (always-on) memang sulit dipisahkan dari baseline pada MMM manapun. Di dunia
   nyata hal ini biasanya diatasi dengan eksperimen (lift test) atau prior yang dikalibrasi,
   dan itu layak disebut di bagian limitasi.
3. **Opsi uji berikutnya:**
   - Simulasi dengan variasi spend yang lebih besar (kampanye berdenyut, bukan konstan) untuk
     menguji H3 secara langsung.
   - Simulasi tiga tahun untuk menambah jumlah siklus musiman dan data.
   - Prior yang lebih ketat atau reparameterisasi supaya saturasi Hill bisa konvergen (H5).
4. **Batasan analisis ini:** satu seed simulasi, dua chain, satu siklus Ramadan dan Harbolnas,
   dan belum ada backtesting out-of-sample.
