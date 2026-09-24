"""
Rehace el análisis |B| ∝ R^n por encuentro de Parker Solar Probe, corrigiendo la
alineación temporal entre efemérides y campo magnético.

Diferencias con "Codigo Nuevo":
  * Los datos se piden a la API HAPI de CDAWeb (sin raspar el árbol de SPDF) y se
    guardan en un caché local en CSV.
  * La distancia R se interpola en el TIEMPO de cada medición de B (np.interp),
    no por índice.
  * Los perihelios se detectan como mínimos de R en la efeméride horaria.
  * El ajuste se hace sobre medianas de log|B| en bins de log R (evita que domine
    la parte lejana de la órbita, donde la sonda pasa más tiempo) y el error se
    estima con bootstrap por bloques diarios.
  * Se calcula el proxy de flujo magnético abierto |B_R| r^2 cerca del perihelio.

Uso:
    pip install -r requirements.txt
    python analisis_encuentros.py          # descarga (~1 GB en CSV) y ajusta
    python analisis_encuentros.py --figuras
"""
import argparse
import os

import numpy as np
import pandas as pd
import requests
from scipy.signal import find_peaks

HAPI = "https://cdaweb.gsfc.nasa.gov/hapi/data"
CACHE = "cache_hapi"
UA_EN_RSOL = 215.03
DIA = 86400.0


def hapi(dataset, parametros, t0, t1):
    """Descarga (o lee del caché) un intervalo HAPI en CSV. Devuelve un DataFrame."""
    os.makedirs(CACHE, exist_ok=True)
    archivo = os.path.join(CACHE, f"{dataset}_{t0[:10]}_{t1[:10]}.csv")
    if not os.path.exists(archivo):
        r = requests.get(HAPI, timeout=900, params={
            "id": dataset, "parameters": parametros, "time.min": t0, "time.max": t1})
        r.raise_for_status()
        with open(archivo, "w") as f:
            f.write(r.text)
    return pd.read_csv(archivo, header=None)


def a_segundos(serie):
    """ISO 8601 (UTC) -> segundos Unix, sin depender de la zona horaria local."""
    return (pd.to_datetime(serie, utc=True) - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds().values


def efemerides():
    df = hapi("PSP_HELIO1HR_POSITION", "RAD_AU,HG_LAT", "2018-08-13T00:00:00Z", "2026-12-31T00:00:00Z")
    df.columns = ["t", "R", "lat"]
    df["s"] = a_segundos(df.t)
    return df


def perihelios(eph):
    i, _ = find_peaks(-eph.R.values, distance=1000, prominence=0.2)
    return eph.iloc[i][["t", "s", "R"]].reset_index(drop=True)


def campo(t0, t1):
    df = hapi("PSP_FLD_L2_MAG_RTN_1MIN", "psp_fld_l2_mag_RTN_1min", t0, t1)
    df.columns = ["t", "BR", "BT", "BN"]
    df = df.dropna()
    df["s"] = a_segundos(df.t)
    df["B"] = np.sqrt(df.BR**2 + df.BT**2 + df.BN**2)
    return df


def ajuste_por_bins(R, B, n_bins=20):
    """Recta en log-log sobre las medianas de log B en bins logarítmicos de R."""
    bordes = np.logspace(np.log10(R.min()), np.log10(R.max()), n_bins + 1)
    g = pd.DataFrame({"k": np.digitize(R, bordes), "x": np.log10(R), "y": np.log10(B)}).groupby("k").median()
    return np.polyfit(g.x, g.y, 1)  # [pendiente, intercepto]


def bootstrap_diario(R, B, s, n=200, rng=np.random.default_rng(0)):
    """Remuestrea días completos: respeta la autocorrelación de las fluctuaciones."""
    dia = (s // DIA).astype(int)
    grupos = [np.flatnonzero(dia == d) for d in np.unique(dia)]
    muestras = []
    for _ in range(n):
        idx = np.concatenate([grupos[j] for j in rng.integers(len(grupos), size=len(grupos))])
        muestras.append(ajuste_por_bins(R[idx], B[idx]))
    return np.std(muestras, axis=0)


def analizar(dias=40, r_flujo=0.25):
    eph = efemerides()
    per = perihelios(eph)
    ultimo_dato = pd.Timestamp("2026-04-30T00:00Z").timestamp()  # fin actual de mag_RTN_1min en CDAWeb
    filas = []
    for k, p in per.iterrows():
        if p.s + (dias + 2) * DIA > ultimo_dato:
            break
        t0 = pd.Timestamp(p.s - (dias + 1) * DIA, unit="s").strftime("%Y-%m-%dT00:00:00Z")
        t1 = pd.Timestamp(p.s + (dias + 2) * DIA, unit="s").strftime("%Y-%m-%dT00:00:00Z")
        mag = campo(t0, t1)
        R = np.interp(mag.s.values, eph.s.values, eph.R.values)  # <- la corrección clave
        tramos = {"acercamiento": (mag.s >= p.s - dias * DIA) & (mag.s <= p.s),
                  "alejamiento": (mag.s >= p.s) & (mag.s <= p.s + dias * DIA)}
        for tramo, m in tramos.items():
            m = m.values
            if m.sum() < 5000:
                continue
            (n, a), (dn, da) = ajuste_por_bins(R[m], mag.B.values[m]), bootstrap_diario(R[m], mag.B.values[m], mag.s.values[m])
            cerca = m & (R < r_flujo)
            filas.append({
                "encuentro": k + 1, "tramo": tramo, "perihelio": p.t[:13],
                "Rmin_Rsol": round(p.R * UA_EN_RSOL, 2), "cobertura": m.sum() / (dias * 1440),
                "n": n, "dn": dn, "log10_B_1UA": a, "dlog10_B_1UA": da,
                "BR_r2_nT_UA2": np.median(np.abs(mag.BR.values[cerca]) * R[cerca] ** 2) if cerca.sum() > 1000 else np.nan,
            })
        print(f"E{k + 1:02d} listo", flush=True)
    res = pd.DataFrame(filas)
    res.to_csv("resultados_por_encuentro.csv", index=False)
    return res


def figuras(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colores = {"acercamiento": "#2a78d6", "alejamiento": "#eb6834"}
    res = res.assign(anio=pd.to_datetime(res.perihelio + ":00").map(lambda d: d.year + (d.dayofyear - 1) / 365.25))
    fig, ax = plt.subplots(3, 1, figsize=(7.5, 8), sharex=True)
    for tramo, d in res.groupby("tramo"):
        c = colores[tramo]
        ax[0].errorbar(d.anio, d.n, d.dn, fmt="o", ms=4.5, color=c, elinewidth=1, label=tramo.capitalize())
        B1 = 10**d.log10_B_1UA
        ax[1].errorbar(d.anio, B1, np.log(10) * B1 * d.dlog10_B_1UA, fmt="o", ms=4.5, color=c, elinewidth=1)
    f = res.groupby("anio").BR_r2_nT_UA2.mean()
    ax[2].plot(f.index, f.values, "o-", ms=4.5, lw=1.5, color="#0b0b0b")
    ax[0].axhline(-2, color="#52514e", lw=1, ls="--")
    ax[0].set_ylabel("Índice n en |B| ∝ Rⁿ")
    ax[0].legend(frameon=False)
    ax[1].set_ylabel("|B| extrapolado a 1 UA [nT]")
    ax[2].set_ylabel(r"$|B_R|\,r^2$ [nT UA$^2$]")
    ax[2].set_xlabel("Año")
    for a in ax:
        a.grid(alpha=0.3)
        a.spines[["top", "right"]].set_visible(False)
    fig.align_ylabels()
    fig.tight_layout()
    fig.savefig("coeficientes_corregidos.png", dpi=150)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--figuras", action="store_true", help="solo rehace las figuras desde el CSV")
    args = ap.parse_args()
    res = pd.read_csv("resultados_por_encuentro.csv") if args.figuras else analizar()
    print(res.round(3).to_string())
    figuras(res)
