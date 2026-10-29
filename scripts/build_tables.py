"""Gabungkan hasil fit jadi tabel perbandingan + data/processed/model_results.csv.

Jalankan setelah scripts.run_experiments selesai: python -m scripts.build_tables
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

R = Path("results")
TAGS = ["multiplicative_notrend", "multiplicative_trend", "additive_notrend", "additive_trend",
        "multiplicative_notrend_ta97", "multiplicative_trend_ta97", "multiplicative_trend_hill"]
LABEL = {
    "multiplicative_notrend": "Multiplikatif, tanpa tren",
    "multiplicative_trend": "Multiplikatif, + tren",
    "additive_notrend": "Aditif, tanpa tren",
    "additive_trend": "Aditif, + tren",
    "multiplicative_notrend_ta97": "Multiplikatif, tanpa tren (target_accept 0,97)",
    "multiplicative_trend_ta97": "Multiplikatif, + tren (target_accept 0,97)",
    "multiplicative_trend_hill": "Multiplikatif, + tren, saturasi Hill (TIDAK KONVERGEN)",
}

rows, per_channel = [], []
for tag in TAGS:
    if not (R / f"summary_{tag}.json").exists():
        continue
    s = json.load(open(R / f"summary_{tag}.json"))
    res = pd.read_csv(R / f"channel_results_{tag}.csv")
    d = s["diagnostics"]
    row = {"model": LABEL[tag], "tag": tag, "waktu_fit_detik": round(s["seconds"]),
           "divergences": d["divergences"], "max_r_hat": round(d["max_r_hat"], 3),
           "min_ess_bulk": round(d["min_ess_bulk"]), "r2_in_sample": round(d["r2_in_sample"], 3),
           "mape_in_sample_%": round(d["mape_in_sample_pct"], 2),
           "total_share_est_%": round(res.est_share.sum() * 100, 1)}
    for v, name in (("with_season", "dgn_musim"), ("no_season", "tanpa_musim")):
        row[f"total_share_true_{name}_%"] = round(res[f"true_share_{v}"].sum() * 100, 1)
        row[f"gap_total_{name}_pt"] = round((res.est_share.sum() - res[f"true_share_{v}"].sum()) * 100, 1)
        row[f"MAE_share_{name}_pt"] = round((res.est_share - res[f"true_share_{v}"]).abs().mean() * 100, 2)
        row[f"MAE_roi_{name}"] = round((res.est_roi - res[f"true_roi_{v}"]).abs().mean(), 2)
        row[f"channel_dlm_hdi_{name}"] = int(res[f"share_in_hdi_{v}"].sum())
        c = s["criteria"][v]
        row[f"K1_diagnostik_{name}"] = c["1_diagnostik_sehat"]
        row[f"K2_hdi_{name}"] = c["2_share_dalam_hdi_>=4_dari_5"]
        row[f"K3_total_{name}"] = c["3_total_share_+-5pt"]
        row[f"K4_roi_order_{name}"] = c["4_urutan_roi_ekstrem"]
    rows.append(row)
    r2 = res.copy(); r2.insert(0, "tag", tag); per_channel.append(r2)

comp = pd.DataFrame(rows)
comp.to_csv(R / "comparison_models.csv", index=False)
pd.concat(per_channel).to_csv(R / "channel_results_all.csv", index=False)

# Deliverable Selasa: fit ulang baseline (multiplikatif, tanpa tren, draws=1000, target_accept 0,97 supaya sehat)
base = pd.read_csv(R / "channel_results_multiplicative_notrend_ta97.csv")
keep = ["channel", "est_share", "share_hdi_low", "share_hdi_high", "est_roi", "roi_hdi_low", "roi_hdi_high",
        "true_share_with_season", "true_share_no_season", "true_roi_with_season", "true_roi_no_season"]
base[keep].round(4).to_csv("data/processed/model_results.csv", index=False)
print(comp.T.to_string())
