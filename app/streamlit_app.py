"""
Explorador de Parker Solar Probe: campo magnético y distancia al Sol por encuentro.

Ejecutar localmente:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import psp_datos as pd_psp

AQUI = Path(__file__).parent
AZUL, NARANJA, TINTA, GRIS = "#2a78d6", "#eb6834", "#0b0b0b", "#8a8984"
TRAMO_COLOR = {"acercamiento": AZUL, "alejamiento": NARANJA}

st.set_page_config(page_title="Explorador PSP", page_icon="☀️", layout="wide")


# ---------------------------------------------------------------- datos (con caché)
@st.cache_data(ttl=24 * 3600, show_spinner="Descargando efemérides de PSP…")
def cargar_posicion():
    return pd_psp.posicion()


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cargar_fin_de_datos():
    try:
        return pd_psp.fin_de_datos()
    except Exception:
        return pd.Timestamp("2026-04-30", tz="UTC")


@st.cache_data(ttl=7 * 24 * 3600, max_entries=12, show_spinner="Descargando campo magnético (FIELDS, 1 min)…")
def cargar_campo(t0, t1):
    return pd_psp.campo(t0, t1, cargar_posicion())


@st.cache_data
def cargar_resultados():
    return pd.read_csv(AQUI / "datos" / "resultados_por_encuentro.csv")


@st.cache_data
def cargar_manchas():
    return pd.read_csv(AQUI / "datos" / "manchas_silso_mensual.csv")


def estilo(fig, alto):
    fig.update_layout(template="plotly_white", height=alto, margin=dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
                      hovermode="x unified", font=dict(size=13))
    fig.update_xaxes(showgrid=True, gridcolor="#ecebe8")
    fig.update_yaxes(showgrid=True, gridcolor="#ecebe8")
    return fig


def anio_decimal(t):
    t = pd.to_datetime(t)
    return t.dt.year + (t.dt.dayofyear - 1) / 365.25


# ---------------------------------------------------------------- barra lateral
pos = cargar_posicion()
per = pd_psp.perihelios(pos)
fin = cargar_fin_de_datos()
ahora = pd.Timestamp.now(tz="UTC")

st.sidebar.title("☀️ Explorador PSP")
etiquetas = {k: f"E{k:02d} · {r.t:%Y-%m-%d} · {r.R * pd_psp.UA_EN_RSOL:.1f} R☉"
             + ("" if r.t < ahora else " (futuro)") for k, r in per.iterrows()}
disponibles = [k for k, r in per.iterrows() if r.t + pd.Timedelta(days=1) < fin]
enc = st.sidebar.selectbox("Encuentro", list(per.index), index=list(per.index).index(disponibles[-1]),
                           format_func=etiquetas.get)
dias = st.sidebar.slider("Ventana alrededor del perihelio [días]", 2, 40, 10)
resol = st.sidebar.select_slider("Promedio para las series de tiempo", ["1 min", "10 min", "1 h"], value="10 min")
st.sidebar.caption(f"Campo magnético disponible en CDAWeb hasta **{fin:%Y-%m-%d}**.")
st.sidebar.markdown("---")
st.sidebar.caption("Datos: NASA/CDAWeb vía HAPI · FIELDS (Bale et al. 2016) · SILSO. "
                   "Código: rama `revision-2026`.")

tp = per.loc[enc, "t"]
t0, t1 = tp - pd.Timedelta(days=dias), min(tp + pd.Timedelta(days=dias), fin)

# ---------------------------------------------------------------- encabezado
st.title(f"Encuentro {enc}: perihelio del {tp:%d-%m-%Y %H:%M} UT")

hay_datos = tp - pd.Timedelta(days=1) < fin
mag = None
if hay_datos:
    try:
        mag = cargar_campo(t0, t1)
    except Exception as e:
        st.error(f"No se pudo descargar el campo magnético desde CDAWeb: {e}")

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Distancia mínima ({per.loc[enc, 'R']:.4f} UA)", f"{per.loc[enc, 'R'] * pd_psp.UA_EN_RSOL:.2f} R☉")
if mag is not None and len(mag):
    c2.metric("|B| máximo (1 min)", f"{mag.B.max():,.0f} nT")
    c3.metric("|B| mediano en la ventana", f"{mag.B.median():,.1f} nT")
    c4.metric("Cobertura de datos", f"{len(mag) / ((t1 - t0).total_seconds() / 60):.0%}")
else:
    c2.info("Sin datos de campo para este encuentro (aún no publicados).")

tab_orb, tab_ser, tab_br, tab_ciclo, tab_info = st.tabs(
    ["🛰️ Órbita", "📈 Series de tiempo", "📉 |B| vs distancia", "🔄 Ciclo solar", "ℹ️ Método y fuentes"])

# ---------------------------------------------------------------- órbita
with tab_orb:
    izq, der = st.columns([3, 2])
    with der:
        dia_rel = st.slider("Posición de la sonda: días desde el perihelio", -dias, dias, 0)
        st.markdown(
            "Plano de la eclíptica en coordenadas **heliocéntricas inerciales (HGI)**. "
            "En gris, la trayectoria completa de la misión; en azul, la ventana elegida. "
            "Cerca del perihelio la sonda casi **co-rota** con el Sol: recorre ~180° de longitud "
            "en pocos días, algo que se aprecia moviendo el deslizador.")
        t_son = tp + pd.Timedelta(days=dia_rel)
        fila = pos.iloc[(pos.t - t_son).abs().argmin()]
        st.metric(f"R el {fila.t:%d-%m-%Y %H:%M} UT", f"{fila.R * pd_psp.UA_EN_RSOL:.1f} R☉ · {fila.R:.3f} UA")
    with izq:
        fig = go.Figure()
        th = np.linspace(0, 2 * np.pi, 361)
        for nombre, a in (("Mercurio", 0.387), ("Venus", 0.723), ("Tierra", 1.0)):
            fig.add_scatter(x=a * np.cos(th), y=a * np.sin(th), mode="lines", line=dict(color="#d9d8d3", width=1),
                            name=nombre, hoverinfo="name", showlegend=False)
            fig.add_annotation(x=a * np.cos(np.pi / 4), y=a * np.sin(np.pi / 4), text=nombre, showarrow=False,
                               font=dict(color=GRIS, size=11), yshift=8)
        pas = pos[pos.t <= ahora]
        fig.add_scatter(x=pas.x, y=pas.y, mode="lines", line=dict(color="#c7c6c0", width=1), name="Misión", hoverinfo="skip")
        v = pos[(pos.t >= tp - pd.Timedelta(days=dias)) & (pos.t <= tp + pd.Timedelta(days=dias))]
        fig.add_scatter(x=v.x, y=v.y, mode="lines", line=dict(color=AZUL, width=3), name="Ventana",
                        customdata=np.c_[v.t.dt.strftime("%Y-%m-%d %H:%M"), v.R],
                        hovertemplate="%{customdata[0]}<br>R = %{customdata[1]:.3f} UA<extra></extra>")
        fig.add_scatter(x=[0], y=[0], mode="markers", marker=dict(size=16, color="#f5b301"), name="Sol", hoverinfo="name")
        fig.add_scatter(x=[fila.x], y=[fila.y], mode="markers", marker=dict(size=11, color=NARANJA, line=dict(color="white", width=2)),
                        name="PSP", hovertemplate=f"PSP · {fila.t:%Y-%m-%d %H:%M}<extra></extra>")
        fig.update_xaxes(range=[-1.1, 1.1], title="x HGI [UA]", zeroline=False)
        fig.update_yaxes(range=[-1.1, 1.1], title="y HGI [UA]", scaleanchor="x", zeroline=False)
        estilo(fig, 620).update_layout(hovermode="closest", showlegend=False)
        st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- series de tiempo
with tab_ser:
    if mag is None or not len(mag):
        st.info("No hay datos de campo magnético para este encuentro.")
    else:
        regla = {"1 min": None, "10 min": "10min", "1 h": "1h"}[resol]
        m = mag.set_index("t")[["B", "R"]]
        if regla:
            m = m.resample(regla).mean()
        escala_log = st.toggle("Escala logarítmica en |B|", value=True)
        fig = go.Figure()
        fig.add_scattergl(x=m.index, y=m.B, mode="lines", line=dict(color=TINTA, width=1.3), name="|B|",
                          customdata=m.R * pd_psp.UA_EN_RSOL,
                          hovertemplate="%{x|%Y-%m-%d %H:%M}<br>|B| = %{y:.1f} nT<br>R = %{customdata:.1f} R☉<extra></extra>")
        fig.add_vline(x=tp, line=dict(color=GRIS, dash="dot", width=1))
        fig.add_annotation(x=tp, y=1, yref="paper", text="perihelio", showarrow=False, yshift=10,
                           font=dict(color=GRIS, size=11))
        fig.update_yaxes(title="|B| [nT]", type="log" if escala_log else "linear", dtick=1 if escala_log else None)
        fig.update_xaxes(title="Tiempo (UT)")
        st.plotly_chart(estilo(fig, 520).update_layout(showlegend=False, hovermode="closest"), width="stretch")
        st.caption(f"Magnitud del campo magnético (promedios de {resol}). Pase el cursor para ver la distancia al Sol "
                   "en cada instante. El crecimiento hacia el perihelio refleja principalmente la caída ~R⁻² del campo; "
                   "las caídas bruscas y breves suelen ser cruces de la lámina de corriente heliosférica, donde |B| se anula "
                   "localmente.")

# ---------------------------------------------------------------- |B| vs R
with tab_br:
    if mag is None or not len(mag):
        st.info("No hay datos de campo magnético para este encuentro.")
    else:
        izq, der = st.columns([3, 1])
        with der:
            V = st.slider("Velocidad del viento para la curva de Parker [km/s]", 200, 800, 400, 50)
            mostrar_parker = st.checkbox("Mostrar espiral de Parker", True)
        with izq:
            fig = go.Figure()
            fig.add_histogram2d(x=np.log10(mag.R), y=np.log10(mag.B), nbinsx=80, nbinsy=80,
                                colorscale="Blues", showscale=False, hoverinfo="skip", name="densidad")
            filas = []
            for tramo, mascara in (("acercamiento", mag.t <= tp), ("alejamiento", mag.t >= tp)):
                d = mag[mascara]
                if len(d) < 500 or d.R.max() / d.R.min() < 1.2:
                    continue
                n, a, g = pd_psp.ajuste_por_bins(d.R.values, d.B.values)
                filas.append((tramo, n, 10**a))
                xx = np.array([d.R.min(), d.R.max()])
                fig.add_scatter(x=np.log10(g.R), y=np.log10(g.B), mode="markers", marker=dict(size=8, color=TRAMO_COLOR[tramo],
                                line=dict(color="white", width=1.5)), name=f"{tramo}: medianas",
                                hovertemplate="R = %{customdata[0]:.3f} UA<br>|B| = %{customdata[1]:.1f} nT<extra></extra>",
                                customdata=np.c_[g.R, g.B])
                fig.add_scatter(x=np.log10(xx), y=a + n * np.log10(xx), mode="lines",
                                line=dict(color=TRAMO_COLOR[tramo], width=2), name=f"{tramo}: n = {n:.2f}")
            if mostrar_parker:
                rr = np.logspace(np.log10(mag.R.min()), np.log10(mag.R.max()), 50)
                r_ref = np.median(mag.R)
                fig.add_scatter(x=np.log10(rr), y=np.log10(pd_psp.parker_B(rr, np.median(mag.B[np.isclose(mag.R, r_ref, rtol=0.05)]), r_ref, V)),
                                mode="lines", line=dict(color=TINTA, dash="dash", width=1.5), name=f"Parker, V = {V} km/s")
            ticks_R = [0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.5]
            ticks_B = [1, 3, 10, 30, 100, 300, 1000, 3000]
            fig.update_xaxes(title="Distancia al Sol R [UA]", tickvals=np.log10(ticks_R), ticktext=ticks_R)
            fig.update_yaxes(title="|B| [nT]", tickvals=np.log10(ticks_B), ticktext=ticks_B)
            st.plotly_chart(estilo(fig, 560).update_layout(hovermode="closest"), width="stretch")
        with der:
            for tramo, n, b1 in filas:
                st.metric(f"n ({tramo})", f"{n:.2f}")
                st.caption(f"|B| extrapolado a 1 UA ≈ {b1:.1f} nT")
            st.caption("Ajuste en log-log sobre medianas por bin de log R, con R interpolada en el tiempo de cada medición. "
                       "Para ventanas cortas el rango en R es pequeño y la pendiente es poco confiable; "
                       "use 30–40 días para comparar con la pestaña *Ciclo solar*.")

# ---------------------------------------------------------------- ciclo solar
with tab_ciclo:
    with st.expander("¿Cómo leer estos gráficos?", expanded=True):
        st.markdown("""
Cada punto resume **un tramo de 40 días** de un encuentro: el **acercamiento** (azul, 40 días antes del perihelio)
o el **alejamiento** (naranja, 40 días después). En cada tramo se ajusta una ley de potencias
**|B| = B₁ · Rⁿ** (R en UA) a la magnitud del campo, igual que en la pestaña *|B| vs distancia*.

1. **Índice n**: qué tan rápido cae |B| al alejarse del Sol. Un campo puramente radial daría n = −2
   (línea discontinua); la espiral de Parker, algo menos empinado. Si n cambiara con la actividad solar,
   se vería una tendencia; aquí se mantiene en ≈ −1,77 durante todo el ciclo.
2. **|B| a 1 UA (B₁)**: el ajuste evaluado en R = 1 UA, es decir, la *intensidad global* del campo del
   viento solar en ese período. **Sí cambia con el ciclo**: ≈ 3,5 nT en el mínimo (2018–2020) y 5–6,5 nT cerca del máximo.
3. **|B_R| r²**: la componente radial escalada por r², que según Parker se conserva con la distancia.
   Es un indicador del **flujo magnético abierto** del Sol (Φ ≈ 4π r² |B_R|). Es la única curva que usa una componente
   y no la magnitud, porque el flujo abierto se define a partir del campo radial.
4. **Número de manchas solares**: el termómetro clásico de la actividad solar (ciclo 25, máximo en 2024–2025).

La idea es comparar los paneles 2 y 3 con el 4: la sonda "ve" el ciclo solar como un aumento de la
intensidad del campo, sin que cambie la forma en que el campo decae con la distancia (panel 1).
""")
    res = cargar_resultados()
    res["anio"] = anio_decimal(res.perihelio + ":00")
    man = cargar_manchas()
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06, subplot_titles=(
        "1 · Índice n de la ley |B| ∝ Rⁿ", "2 · |B| extrapolado a 1 UA", "3 · Proxy de flujo abierto |B_R| r²",
        "4 · Número de manchas solares (actividad)"))
    fig.update_annotations(font=dict(size=13, color=TINTA), x=0, xanchor="left")
    for tramo, d in res.groupby("tramo"):
        c = TRAMO_COLOR[tramo]
        comun = dict(mode="markers", marker=dict(size=8, color=c, line=dict(color="white", width=1)),
                     legendgroup=tramo, customdata=d.encuentro)
        fig.add_scatter(x=d.anio, y=d.n, error_y=dict(array=d.dn, color=c, thickness=1, width=0), name=tramo.capitalize(),
                        hovertemplate="E%{customdata}: n = %{y:.2f}<extra></extra>", row=1, col=1, **comun)
        b1 = 10**d.log10_B_1UA
        fig.add_scatter(x=d.anio, y=b1, error_y=dict(array=np.log(10) * b1 * d.dlog10_B_1UA, color=c, thickness=1, width=0),
                        showlegend=False, hovertemplate="E%{customdata}: %{y:.2f} nT<extra></extra>", row=2, col=1, **comun)
    f = res.groupby(["encuentro", "anio"], as_index=False).BR_r2_nT_UA2.mean()
    fig.add_scatter(x=f.anio, y=f.BR_r2_nT_UA2, mode="lines+markers", line=dict(color=TINTA, width=1.5), marker=dict(size=7),
                    name="|B_R| r²", customdata=f.encuentro, hovertemplate="E%{customdata}: %{y:.2f} nT UA²<extra></extra>",
                    row=3, col=1)
    fig.add_scatter(x=man.anio_decimal, y=man.manchas, mode="lines", line=dict(color=GRIS, width=1.5),
                    name="Manchas (SILSO)", hovertemplate="%{y:.0f}<extra></extra>", row=4, col=1)
    fig.add_hline(y=-2, line=dict(color=GRIS, dash="dash", width=1), row=1, col=1)
    sel = res[res.encuentro == enc]
    if len(sel):
        fig.add_vline(x=sel.anio.iloc[0], line=dict(color=NARANJA, width=1, dash="dot"))
    fig.update_yaxes(title="n en |B| ∝ Rⁿ", row=1, col=1)
    fig.update_yaxes(title="|B| a 1 UA [nT]", row=2, col=1)
    fig.update_yaxes(title="|B_R| r² [nT UA²]", row=3, col=1)
    fig.update_yaxes(title="Nº manchas", row=4, col=1)
    fig.update_xaxes(title="Año", row=4, col=1)
    st.plotly_chart(estilo(fig, 950).update_layout(hovermode="closest", margin=dict(t=90), legend=dict(y=1.07)), width="stretch")
    st.caption("Resultados precalculados con `Codigo Propuesto/analisis_encuentros.py` (ventanas de ±40 días, "
               "barras de error por bootstrap de bloques diarios). La línea punteada naranja marca el encuentro elegido. "
               "|B_R| r² es un proxy del flujo magnético abierto, calculado con r < 0,25 UA.")
    with st.expander("Ver tabla"):
        st.dataframe(res.drop(columns="anio").round(3), width="stretch", hide_index=True)

# ---------------------------------------------------------------- información
with tab_info:
    st.markdown("""
### Qué muestra esta app
Mediciones del magnetómetro **FIELDS** de Parker Solar Probe (promedios de 1 minuto, coordenadas RTN)
y la posición de la sonda, ambos descargados en vivo desde **CDAWeb** mediante la API **HAPI**.

- **R** se interpola en el tiempo de cada medición de campo (efeméride horaria `PSP_HELIO1HR_POSITION`).
- Los **perihelios** se detectan como mínimos locales de R.
- El **ajuste |B| ∝ Rⁿ** se hace sobre las medianas de log|B| en 20 bins logarítmicos de R,
  separando acercamiento y alejamiento.
- La **espiral de Parker**: |B| ∝ r⁻² √(1 + (Ωr/V)²), normalizada a la mediana observada.

**Limitaciones del prototipo:** el producto HAPI de 1 min no incluye *quality flags*;
no se separan eyecciones de masa coronal ni tipos de viento.

### Fuentes y referencias
- Datos: [CDAWeb](https://cdaweb.gsfc.nasa.gov) · `PSP_FLD_L2_MAG_RTN_1MIN`, `PSP_HELIO1HR_POSITION`.
  Bale, S. D. et al. (2016), *The FIELDS Instrument Suite for Solar Probe Plus*, Space Sci. Rev. 204, 49.
- Weigel, R. S. et al. (2021), *HAPI: An API Standard for Accessing Heliophysics Time Series Data*, JGR Space Physics 126.
  [doi:10.1029/2021JA029534](https://doi.org/10.1029/2021JA029534)
- Badman, S. T. et al. (2021), *Measurement of the open magnetic flux in the inner heliosphere down to 0.13 AU*, A&A 650, A18.
- Gieseler, J. et al. (2023), *Solar-MACH: An open-source tool to analyze solar magnetic connection configurations*,
  Front. Astron. Space Sci. 9, 1058810 — inspiración para esta app.
- Número de manchas: SILSO, Royal Observatory of Belgium.
""")
