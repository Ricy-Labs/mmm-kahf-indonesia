"""Jalankan fit untuk kombinasi (mode data x tren) dan simpan hasilnya.

Contoh:
    python -m scripts.run_experiments --mode multiplicative --trend 0   # fit ulang draws=1000
    python -m scripts.run_experiments --mode multiplicative --trend 1   # + komponen tren
    python -m scripts.run_experiments --mode additive --trend 0
    python -m scripts.run_experiments --mode additive --trend 1
"""
import argparse, json, time, warnings
from pathlib import Path

import pandas as pd

from src.data_loader import load_data
from src.modeling import channel_results, check_criteria, diagnostics, fit_mmm
from src.simulate_data import DEFAULT_PATHS

warnings.filterwarnings("ignore")

ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=["multiplicative", "additive"], default="multiplicative")
ap.add_argument("--trend", type=int, default=0)
ap.add_argument("--draws", type=int, default=1000)
ap.add_argument("--target_accept", type=float, default=0.9)
ap.add_argument("--saturation", choices=["logistic", "hill"], default="logistic")
ap.add_argument("--suffix", default="")
args = ap.parse_args()

data_path, truth_path = DEFAULT_PATHS[args.mode]
df = load_data(data_path)
truth = pd.read_csv(truth_path)
tag = f"{args.mode}_{'trend' if args.trend else 'notrend'}{args.suffix}"

t0 = time.time()
mmm = fit_mmm(df, trend=bool(args.trend), saturation=args.saturation,
               draws=args.draws, target_accept=args.target_accept, progressbar=False)
secs = time.time() - t0

out = Path("results"); out.mkdir(exist_ok=True)
mmm.idata.to_netcdf(out / f"idata_{tag}.nc")   # simpan fit dulu, sebelum hitung apa-apa

diag = diagnostics(mmm, df)
res = channel_results(mmm, df, truth)
crit = {v: check_criteria(diag, res, v) for v in ("with_season", "no_season")}

res.to_csv(out / f"channel_results_{tag}.csv", index=False)
json.dump({"tag": tag, "seconds": secs, "diagnostics": diag, "criteria": crit}, open(out / f"summary_{tag}.json", "w"), indent=2)
print(tag, f"{secs:.0f}s"); print(json.dumps(diag, indent=1)); print(res.round(3).T)
