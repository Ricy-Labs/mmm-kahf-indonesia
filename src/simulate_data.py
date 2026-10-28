from pathlib import Path

import numpy as np
import pandas as pd

from src.config import CHANNEL_COLS, DATE_COL, SAT_MULT, SIM_PARAMS, TARGET_COL
from src.transforms import geometric_adstock, hill_saturation

FLAGS_PATH = Path("data/raw/calendar_flags.csv")
FLAG_COLS = ["ramadan_flag", "harbolnas_flag", "payday_flag"]
RAMADAN_FALLBACK = [("2025-03-01", "2025-03-30")]  # perkiraan, dipakai kalau file flag tidak ada


def _calendar_flags(dates):
    """Pakai flag buatan DS kalau ada, kalau tidak hitung perkiraan dari aturan di asumsi.md."""
    if FLAGS_PATH.exists():
        f = pd.read_csv(FLAGS_PATH)
        if DATE_COL not in f.columns:
            raise ValueError(f"Kolom '{DATE_COL}' tidak ada di {FLAGS_PATH}. Kolom yang ada: {list(f.columns)}")
        missing = [c for c in FLAG_COLS if c not in f.columns]
        if missing:
            raise ValueError(f"Kolom flag tidak ada di {FLAGS_PATH}: {missing}. Kolom yang ada: {list(f.columns)}")
        f[DATE_COL] = pd.to_datetime(f[DATE_COL])
        f = f.set_index(DATE_COL).reindex(dates)
        if f[FLAG_COLS].isna().any().any():
            raise ValueError("Flag kalender tidak menutupi semua tanggal simulasi.")
        return f[FLAG_COLS].astype(int).reset_index(drop=True)

    ramadan = np.zeros(len(dates), dtype=int)
    for a, b in RAMADAN_FALLBACK:
        ramadan |= ((dates >= a) & (dates <= b)).astype(int)
    harbolnas = (((dates.month == 11) & (dates.day == 11)) |
                 ((dates.month == 12) & (dates.day == 12))).astype(int)
    payday = ((dates.day >= 25) | (dates.day == 1)).astype(int)
    return pd.DataFrame({"ramadan_flag": ramadan, "harbolnas_flag": harbolnas, "payday_flag": payday})


MODES = ("multiplicative", "additive")
DEFAULT_PATHS = {
    "multiplicative": ("data/raw/mmm_kahf_simulated.csv", "data/processed/true_contributions.csv"),
    "additive": ("data/raw/mmm_kahf_simulated_additive.csv", "data/processed/true_contributions_additive.csv"),
}


def simulate(mode="multiplicative", out_path=None, truth_path=None):
    """Simulasi data harian.

    mode="multiplicative" (default, struktur utama): efek kalender MENGALIKAN seluruh penjualan
        (baseline + media + kompetitor). Hasilnya identik dengan data versi sebelumnya.
    mode="additive" (pembanding): efek kalender DITAMBAHKAN sebagai angka tetap, besarnya
        lift x rata-rata penjualan pra-musim, jadi media tidak ikut "dikali" musim.
        Spend, kompetitor, dan noise memakai seed yang sama dengan mode multiplikatif.

    Jawaban benar dihitung dua versi:
        - true_contribution_share : kontribusi media DENGAN pengali musim (bagian musim yang
          menempel di media ikut dihitung sebagai kontribusi media)
        - true_share_no_season    : kontribusi media TANPA pengali musim (efek media mentah)
      Di mode aditif kedua versi sama, karena tidak ada pengali musim.
    """
    if mode not in MODES:
        raise ValueError(f"mode harus salah satu dari {MODES}, bukan '{mode}'")
    default_out, default_truth = DEFAULT_PATHS[mode]
    out_path = out_path or default_out
    truth_path = truth_path or default_truth

    p = SIM_PARAMS
    rng = np.random.default_rng(p["seed"])
    dates = pd.date_range(p["start_date"], periods=p["n_days"], freq="D")
    n = len(dates)

    flags = _calendar_flags(dates)
    ram = flags["ramadan_flag"].values
    har = flags["harbolnas_flag"].values
    pay = flags["payday_flag"].values
    weekend = (dates.dayofweek >= 5).astype(int)

    df = pd.DataFrame({DATE_COL: dates})
    boost = 1 + 0.2 * np.maximum(ram, har)  # budget naik sedikit pas musim ramai

    media = {}
    for col, cfg in p["channels"].items():
        spend = cfg["mean"] * rng.gamma(4.0, 0.25, n) * boost
        if col == "marketplace_ads_S":       # naik tajam saat Harbolnas
            spend = spend * (1 + 2.0 * har)
        if col == "offline_activation_S":    # lonjakan event, sebagian besar hari nol
            event = rng.random(n) < 0.04
            spend = np.where(event, cfg["mean"] * 12 * rng.uniform(0.7, 1.3, n), 0.0)

        decay = 0.5 ** (1 / cfg["half_life"])
        ad = geometric_adstock(spend, decay, l_max=28)
        half_sat = SAT_MULT[cfg["sat"]] * ad.mean()
        media[col] = cfg["beta"] * hill_saturation(ad, half_sat)
        df[col] = spend.round(2)

    competitor = 450 + np.cumsum(rng.normal(0, 4, n))
    competitor_effect = p["competitor_effect"] * (competitor - 450)

    season_lift = (p["ramadan_lift"] * ram + p["harbolnas_lift"] * har
                   + p["payday_lift"] * pay + p["weekend_lift"] * weekend)
    baseline = p["base_sales"] + p["trend_per_day"] * np.arange(n)
    pre_season = baseline + sum(media.values()) + competitor_effect
    if mode == "multiplicative":
        season_mult = 1 + season_lift
        sales = pre_season * season_mult
    else:
        season_mult = np.ones(n)                       # tidak ada pengali musim
        sales = pre_season + season_lift * pre_season.mean()
    sales = sales + rng.normal(0, p["noise_sd"], n)

    df["ramadan_flag"] = ram
    df["harbolnas_flag"] = har
    df["payday_flag"] = pay
    df["weekend_flag"] = weekend
    df["competitor_sales_B"] = competitor.round(2)
    df[TARGET_COL] = np.clip(sales, 0, None).round(2)

    # Jawaban benar buat backtesting (2 versi): dengan dan tanpa pengali musim
    total = df[TARGET_COL].sum()
    with_season = np.array([(media[c] * season_mult).sum() for c in CHANNEL_COLS])
    no_season = np.array([media[c].sum() for c in CHANNEL_COLS])
    spend_total = np.array([df[c].sum() for c in CHANNEL_COLS])
    truth = pd.DataFrame({
        "channel": CHANNEL_COLS,
        "true_contribution_share": with_season / total,
        "true_share_no_season": no_season / total,
        "spend_total": spend_total,
        "true_roi": with_season / spend_total,
        "true_roi_no_season": no_season / spend_total,
    })

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(truth_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    truth.to_csv(truth_path, index=False)
    return df, truth


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Simulasi data MMM Kahf")
    ap.add_argument("--mode", choices=list(MODES) + ["both"], default="multiplicative")
    args = ap.parse_args()
    for m in (MODES if args.mode == "both" else [args.mode]):
        data, truth = simulate(mode=m)
        print(f"== mode: {m} ==")
        print(data.head())
        print(truth.round(4))
