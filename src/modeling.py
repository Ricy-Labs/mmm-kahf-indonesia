"""Helper fit + evaluasi model MMM (PyMC-Marketing) untuk data simulasi Kahf.

Dipakai oleh notebooks/03_refit_trend_backtest_ricy.ipynb dan scripts/run_experiments.py.
"""
import arviz as az
import numpy as np
import pandas as pd

from src.config import CHANNEL_COLS, CONTROL_COLS, DATE_COL, TARGET_COL

HDI_PROB = 0.94


def hdi(samples, prob=HDI_PROB):
    """Interval kredibel terpendek (HDI) dari sampel 1D. Ditulis sendiri supaya tidak tergantung versi arviz."""
    x = np.sort(np.asarray(samples).reshape(-1))
    n = len(x)
    k = int(np.ceil(prob * n))
    widths = x[k - 1:] - x[: n - k + 1]
    i = int(np.argmin(widths))
    return float(x[i]), float(x[i + k - 1])
SAMPLER = dict(chains=2, cores=2, draws=1000, tune=1000, target_accept=0.9, random_seed=42)


def build_xy(df, trend=False):
    """Pisahkan X dan y. trend=True menambah kolom `trend` (indeks waktu 0-1) sebagai kontrol."""
    X = df.drop(columns=[TARGET_COL]).copy()
    controls = list(CONTROL_COLS)
    if trend:
        X["trend"] = np.linspace(0.0, 1.0, len(X))
        controls.append("trend")
    y = df[TARGET_COL].rename("y")
    return X, y, controls


def fit_mmm(df, trend=False, saturation="logistic", **sampler_kwargs):
    from pymc_marketing.mmm import MMM, GeometricAdstock, HillSaturation, LogisticSaturation

    X, y, controls = build_xy(df, trend)
    mmm = MMM(
        date_column=DATE_COL,
        channel_columns=CHANNEL_COLS,
        control_columns=controls,
        adstock=GeometricAdstock(l_max=28),
        saturation=HillSaturation() if saturation == "hill" else LogisticSaturation(),
        yearly_seasonality=2,
    )
    kw = {**SAMPLER, **sampler_kwargs}
    mmm.fit(X, y, **kw)
    return mmm


def _contrib_original_scale(mmm):
    """Kontribusi channel per hari per draw, skala asli (chain, draw, date, channel)."""
    post = mmm.idata.posterior
    return post["channel_contribution"] * mmm.idata.constant_data["target_scale"]


def diagnostics(mmm, df):
    """Diagnostik sampler + kecocokan in-sample (R2, MAPE dari rata-rata posterior)."""
    idata = mmm.idata
    div = int(idata.sample_stats["diverging"].sum())
    params = [v for v in ["saturation_beta", "saturation_lam", "saturation_kappa", "saturation_slope",
                          "adstock_alpha", "y_sigma"] if v in idata.posterior]
    summ = az.summary(idata, var_names=params)
    mu = (idata.posterior["mu"] * idata.constant_data["target_scale"]).mean(("chain", "draw")).values
    y = df[TARGET_COL].values
    ss_res, ss_tot = ((y - mu) ** 2).sum(), ((y - y.mean()) ** 2).sum()
    return {
        "divergences": div,
        "max_r_hat": float(summ["r_hat"].max()),
        "min_ess_bulk": float(summ["ess_bulk"].min()),
        "r2_in_sample": float(1 - ss_res / ss_tot),
        "mape_in_sample_pct": float(np.mean(np.abs((y - mu) / y)) * 100),
    }


def channel_results(mmm, df, truth):
    """Share, ROI, dan interval kredibel (HDI 94%) per channel, dibandingkan dengan jawaban benar.

    share = kontribusi channel / total sales. ROI = kontribusi channel / total spend channel.
    """
    contrib = _contrib_original_scale(mmm).sum("date")              # (chain, draw, channel)
    total_sales = df[TARGET_COL].sum()
    spend = df[CHANNEL_COLS].sum()
    rows = []
    for ch in CHANNEL_COLS:
        c = contrib.sel(channel=ch).values.reshape(-1)
        share, roi = c / total_sales, c / spend[ch]
        sh_lo, sh_hi = hdi(share)
        roi_lo, roi_hi = hdi(roi)
        t = truth.set_index("channel").loc[ch]
        rows.append({
            "channel": ch,
            "est_share": share.mean(), "share_hdi_low": sh_lo, "share_hdi_high": sh_hi,
            "est_roi": roi.mean(), "roi_hdi_low": roi_lo, "roi_hdi_high": roi_hi,
            "true_share_with_season": t["true_contribution_share"],
            "true_share_no_season": t["true_share_no_season"],
            "true_roi_with_season": t["true_roi"],
            "true_roi_no_season": t["true_roi_no_season"],
        })
    out = pd.DataFrame(rows)
    for v in ("with_season", "no_season"):
        out[f"share_in_hdi_{v}"] = (out[f"true_share_{v}"] >= out.share_hdi_low) & (out[f"true_share_{v}"] <= out.share_hdi_high)
        out[f"roi_in_hdi_{v}"] = (out[f"true_roi_{v}"] >= out.roi_hdi_low) & (out[f"true_roi_{v}"] <= out.roi_hdi_high)
    return out


def check_criteria(diag, res, version="with_season"):
    """4 kriteria lanjut ke dashboard (usulan Samuel). `version` = versi jawaban benar yang dipakai."""
    total_est = res.est_share.sum()
    total_true = res[f"true_share_{version}"].sum()
    roi_rank = res.set_index("channel").est_roi
    # urutan ROI ekstrem: offline & TikTok harus di atas influencer
    order_ok = (roi_rank["offline_activation_S"] > roi_rank["influencer_S"]
                and roi_rank["tiktok_ads_S"] > roi_rank["influencer_S"])
    return {
        "1_diagnostik_sehat": bool(diag["divergences"] == 0 and diag["max_r_hat"] <= 1.01 and diag["min_ess_bulk"] > 400),
        "2_share_dalam_hdi_>=4_dari_5": bool(res[f"share_in_hdi_{version}"].sum() >= 4),
        "3_total_share_+-5pt": bool(abs(total_est - total_true) <= 0.05),
        "4_urutan_roi_ekstrem": bool(order_ok),
        "total_share_est": float(total_est),
        "total_share_true": float(total_true),
        "n_channel_dalam_hdi": int(res[f"share_in_hdi_{version}"].sum()),
    }
