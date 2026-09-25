"""Acceso a datos de Parker Solar Probe vía HAPI (CDAWeb) y utilidades de análisis."""
import io

import numpy as np
import pandas as pd
import requests
from scipy.signal import find_peaks

HAPI = "https://cdaweb.gsfc.nasa.gov/hapi"
MAG = "PSP_FLD_L2_MAG_RTN_1MIN"
POS = "PSP_HELIO1HR_POSITION"
UA_KM = 1.495978707e8
UA_EN_RSOL = 215.03
OMEGA_SOL = 2.865e-6  # rad/s, rotación sideral (~25,4 d)


def _get(ruta, **params):
    r = requests.get(f"{HAPI}/{ruta}", params=params, timeout=300)
    r.raise_for_status()
    return r


def segundos(t):
    """Segundos Unix de una serie datetime UTC (independiente de la resolución ns/us/ms)."""
    return (t - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds().values


def fin_de_datos(dataset=MAG):
    """Última fecha disponible del dataset según el catálogo HAPI."""
    return pd.Timestamp(_get("info", id=dataset).json()["stopDate"])


def hapi_csv(dataset, parametros, t0, t1, columnas):
    r = _get("data", id=dataset, parameters=parametros, format="csv",
             **{"time.min": t0.strftime("%Y-%m-%dT%H:%M:%SZ"), "time.max": t1.strftime("%Y-%m-%dT%H:%M:%SZ")})
    df = pd.read_csv(io.StringIO(r.text), header=None, names=columnas)
    df["t"] = pd.to_datetime(df["t"], utc=True)
    return df


def posicion():
    """Efeméride horaria de toda la misión (incluye predicción futura)."""
    df = hapi_csv(POS, "RAD_AU,HGI_LAT,HGI_LON", pd.Timestamp("2018-08-13", tz="UTC"),
                  pd.Timestamp("2029-01-31", tz="UTC"), ["t", "R", "lat", "lon"])
    df["x"] = df.R * np.cos(np.radians(df.lat)) * np.cos(np.radians(df.lon))
    df["y"] = df.R * np.cos(np.radians(df.lat)) * np.sin(np.radians(df.lon))
    return df


def perihelios(pos):
    i, _ = find_peaks(-pos.R.values, distance=1000, prominence=0.2)
    p = pos.iloc[i][["t", "R"]].reset_index(drop=True)
    p.index = p.index + 1
    p.index.name = "encuentro"
    return p


def campo(t0, t1, pos):
    """Campo RTN a 1 min, con |B| y la distancia R interpolada EN EL TIEMPO."""
    df = hapi_csv(MAG, "psp_fld_l2_mag_RTN_1min", t0, t1, ["t", "BR", "BT", "BN"]).dropna()
    df["B"] = np.sqrt(df.BR**2 + df.BT**2 + df.BN**2)
    df["R"] = np.interp(segundos(df.t), segundos(pos.t), pos.R.values)
    return df


def ajuste_por_bins(R, B, n_bins=20):
    """Recta log|B| = n log R + a sobre medianas en bins logarítmicos de R."""
    bordes = np.logspace(np.log10(R.min()), np.log10(R.max()), n_bins + 1)
    g = (pd.DataFrame({"k": np.digitize(R, bordes), "R": R, "B": B})
         .groupby("k").median())
    n, a = np.polyfit(np.log10(g.R), np.log10(g.B), 1)
    return n, a, g


def parker_B(R, B_ref, R_ref, V_kms):
    """|B| de la espiral de Parker normalizada a B_ref en R_ref (R en UA)."""
    def forma(r):
        x = OMEGA_SOL * r * UA_KM / V_kms
        return r**-2 * np.sqrt(1 + x**2)
    return B_ref * forma(np.asarray(R)) / forma(R_ref)
