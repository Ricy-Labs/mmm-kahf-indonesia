# src/config.py
# Draft mapping: kolom dataset Robyn (dt_simulated_weekly) -> nama versi Kahf
# Data tetap simulasi, ini cuma relabel konteks.

COLUMN_MAP = {
    "DATE": "date",
    "revenue": "sales",

    # Paid media (spend)
    "tv_S": "influencer_S",            # mega-influencer & kampanye bertema
    "facebook_S": "instagram_ads_S",   # Instagram Ads
    "search_S": "marketplace_ads_S",   # Shopee/Tokopedia Ads
    "print_S": "tiktok_ads_S",         # TikTok Ads
    "ooh_S": "offline_activation_S",   # pop-up / aktivasi offline

    # Metrik pendamping (impressions, clicks)
    "facebook_I": "instagram_ads_I",
    "search_clicks_P": "marketplace_ads_clicks_P",

    # Variabel kontrol
    "competitor_sales_B": "competitor_sales_B", 
    "newsletter": "crm_broadcast",     # WhatsApp/email broadcast
    "events": "event_flag",
}

PAID_MEDIA_SPENDS = [
    "influencer_S", "instagram_ads_S", "marketplace_ads_S",
    "tiktok_ads_S", "offline_activation_S",
]

# Tambahan dari kalender (diisi Data Scientist):
EXTRA_CONTROLS = ["ramadan_flag", "harbolnas_flag", "payday_flag"]

# ---- Kontrak data ----
DATE_COL = "date"
TARGET_COL = "sales"
CHANNEL_COLS = PAID_MEDIA_SPENDS
CONTROL_COLS = ["ramadan_flag", "harbolnas_flag", "payday_flag",
                "weekend_flag", "competitor_sales_B"]

# ---- Parameter simulasi (sumber: docs/asumsi.md) ----
SAT_MULT = {"cepat": 0.5, "sedang": 1.0, "lambat": 2.0}  # pengali titik setengah jenuh

SIM_PARAMS = {
    "seed": 42,
    "start_date": "2025-01-01",
    "n_days": 365,
    "base_sales": 400.0,
    "trend_per_day": 0.1,
    "noise_sd": 20.0,
    "ramadan_lift": 0.20,
    "harbolnas_lift": 0.40,
    "payday_lift": 0.08,
    "weekend_lift": 0.05,
    "competitor_effect": -0.1,
    # half_life dalam hari, sat = kecepatan jenuh, beta = besar efek
    "channels": {
        "tiktok_ads_S":         dict(mean=15, half_life=2,  sat="cepat",  beta=100),
        "instagram_ads_S":      dict(mean=25, half_life=3,  sat="sedang", beta=120),
        "marketplace_ads_S":    dict(mean=30, half_life=2,  sat="sedang", beta=150),
        "influencer_S":         dict(mean=40, half_life=7,  sat="sedang", beta=180),
        "offline_activation_S": dict(mean=8,  half_life=10, sat="lambat", beta=60),
    },
}