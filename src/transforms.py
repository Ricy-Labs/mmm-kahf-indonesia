import numpy as np


def geometric_adstock(x, decay, l_max=8):
    """Efek iklan minggu ini bertahan ke minggu-minggu berikutnya, turun tiap minggu sebesar `decay`."""
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    for t in range(len(x)):
        for lag in range(min(l_max, t + 1)):
            out[t] += x[t - lag] * decay**lag
    return out


def hill_saturation(x, half_sat):
    """Makin besar spend, tambahan hasilnya makin kecil. Nilai 0 sampai 1."""
    x = np.asarray(x, dtype=float)
    return x / (x + half_sat)