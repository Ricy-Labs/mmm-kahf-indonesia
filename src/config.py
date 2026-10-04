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