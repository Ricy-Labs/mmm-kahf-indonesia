from pathlib import Path

import pandas as pd

from src.config import CHANNEL_COLS, COLUMN_MAP, CONTROL_COLS, DATE_COL, TARGET_COL

DEFAULT_PATH = "data/raw/mmm_kahf_simulated.csv"


def load_data(path=DEFAULT_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}. Jalankan python -m src.simulate_data dulu.")

    df = pd.read_csv(path)
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})

    required = [DATE_COL, TARGET_COL] + CHANNEL_COLS + CONTROL_COLS
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ada: {missing}")

    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    df = df.sort_values(DATE_COL).reset_index(drop=True)

    if df[DATE_COL].duplicated().any():
        raise ValueError("Ada tanggal duplikat.")
    if (df[DATE_COL].diff().dropna() != pd.Timedelta(days=1)).any():
        raise ValueError("Ada hari yang loncat, data harus tepat harian.")
    if df[required].isna().any().any():
        raise ValueError("Ada nilai kosong.")
    if (df[CHANNEL_COLS] < 0).any().any():
        raise ValueError("Ada spend negatif.")

    return df[required]