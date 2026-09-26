"""
Explorador de Parker Solar Probe: campo magnético y distancia al Sol por encuentro.

Ejecutar localmente:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import psp_datos as pd_psp

AQUI = Path(__file__).parent
# Paleta de alto contraste basada en la del proyecto original (azul/rojo para acercamiento/alejamiento,
# negro para ajustes y modelos, "plasma" para densidades). Validada: ΔE ≥ 26 entre azul y rojo incluso
# con daltonismo, y contraste ≥ 3:1 sobre el fondo.
AZUL, ROJO, TINTA, GRIS, GRIS_CLARO = "#0b5cd5", "#d62828", "#111111", "#555555", "#d4d4d4"
TRAMO_COLOR = {"acercamiento": AZUL, "alejamiento": ROJO}
PLASMA = [[0.0, "#0d0887"], [0.14, "#46039f"], [0.29, "#7201a8"], [0.43, "#9c179e"], [0.57, "#bd3786"],
          [0.71, "#d8576b"], [0.86, "#ed7953"], [1.0, "#fb9f3a"]]  # plasma sin el tramo amarillo (poco visible sobre blanco)

st.set_page_config(page_title="Explorador PSP", page_icon="☀️", layout="wide", initial_sidebar_state="collapsed")

# Detección de teléfono por User-Agent: ajusta alturas de gráficos y desactiva el arrastre (zoom/pan),
# que en pantallas táctiles impide desplazar la página. El resto del diseño se adapta con CSS.
_ua = st.context.headers.get("User-Agent", "") or ""
ES_MOVIL = bool(re.search(r"Mobi|Android|iPhone|iPod", _ua))

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
h1.titulo {font-size: clamp(1.35rem, 4.5vw, 2.3rem); line-height: 1.2; margin: 0 0 .25rem 0; padding: 0;}
.kpis {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .6rem; margin: .5rem 0 1rem 0;}
.kpi {background: #f1f0ec; border-radius: 10px; padding: .6rem .8rem;}
.kpi .etq {font-size: .8rem; color: #52514e;}
.kpi .val {font-size: clamp(1.15rem, 4vw, 1.6rem); font-weight: 600; color: #0b0b0b; line-height: 1.3;}
.kpi .sub {font-size: .75rem; color: #6b6a66;}
@media (max-width: 640px) {
  .block-container {padding-left: .8rem; padding-right: .8rem; padding-top: 1rem;}
  .kpis {grid-template-columns: repeat(2, 1fr);}
  button[data-baseweb="tab"] {padding-left: .35rem; padding-right: .35rem;}
}
</style>
""", unsafe_allow_html=True)


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


def estilo(fig, alto, alto_movil=None):
    fig.update_layout(template="plotly_white", height=(alto_movil or alto) if ES_MOVIL else alto,
                      margin=dict(l=4, r=4, t=30, b=4) if ES_MOVIL else dict(l=10, r=10, t=30, b=10),
                      legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, font=dict(size=11 if ES_MOVIL else 12)),
                      hovermode="closest", font=dict(size=11 if ES_MOVIL else 13),
                      dragmode=False if ES_MOVIL else "zoom")
    ejes = dict(showgrid=True, gridcolor=GRIS_CLARO, gridwidth=1, automargin=True, showline=True, linecolor=TINTA,
                linewidth=1, mirror=True, ticks="outside", tickcolor=TINTA, tickfont=dict(color=TINTA),
                title_font=dict(color=TINTA), zeroline=False)
    fig.update_xaxes(**ejes)
    fig.update_yaxes(**ejes)
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)", font_color=TINTA)
    return fig


CONFIG_PLOTLY = {"displaylogo": False, "scrollZoom": False, "responsive": True,
                 "displayModeBar": not ES_MOVIL, "doubleClick": "reset"}


def mostrar(fig):
    st.plotly_chart(fig, width="stretch", config=CONFIG_PLOTLY)


def kpis(items):
    """Tarjetas de métricas en grilla CSS: 4 columnas en escritorio, 2 en teléfono."""
    html = "".join(f'<div class="kpi"><div class="etq">{e}</div><div class="val">{v}</div>'
                   + (f'<div class="sub">{s}</div>' if s else "") + "</div>" for e, v, s in items)
    st.markdown(f'<div class="kpis">{html}</div>', unsafe_allow_html=True)


def anio_decimal(t):
    t = pd.to_datetime(t)
    return t.dt.year + (t.dt.dayofyear - 1) / 365.25


# ---------------------------------------------------------------- barra lateral
pos = cargar_posicion()
per = pd_psp.perihelios(pos)
fin = cargar_fin_de_datos()
ahora = pd.Timestamp.now(tz="UTC")

etiquetas = {k: f"E{k:02d} · {r.t:%Y-%m-%d} · {r.R * pd_psp.UA_EN_RSOL:.1f} R☉"
             + ("" if r.t < ahora else " (futuro)") for k, r in per.iterrows()}
disponibles = [k for k, r in per.iterrows() if r.t + pd.Timedelta(days=1) < fin]

st.markdown("##### ☀️ Explorador de Parker Solar Probe")
with st.container(border=True):
    c_enc, c_dias, c_res = st.columns([2, 1.3, 1])
    enc = c_enc.selectbox("Encuentro", list(per.index), index=list(per.index).index(disponibles[-1]),
                          format_func=etiquetas.get)
    dias = c_dias.slider("Ventana alrededor del perihelio [días]", 2, 40, 10)
    resol = c_res.select_slider("Promedio de la serie |B|(t)", ["1 min", "10 min", "1 h"], value="10 min")

tp = per.loc[enc, "t"]
t0, t1 = tp - pd.Timedelta(days=dias), min(tp + pd.Timedelta(days=dias), fin)

# ---------------------------------------------------------------- encabezado
st.markdown(f'<h1 class="titulo">Encuentro {enc} · perihelio {tp:%d-%m-%Y %H:%M} UT</h1>', unsafe_allow_html=True)

hay_datos = tp - pd.Timedelta(days=1) < fin
mag = None
if hay_datos:
    try:
        mag = cargar_campo(t0, t1)
    except Exception as e:
        st.error(f"No se pudo descargar el campo magnético desde CDAWeb: {e}")

# Ajuste |B| = B1·R^n por tramo (acercamiento / alejamiento) de la ventana elegida
ajustes = {}
if mag is not None and len(mag):
    for tramo, mascara in (("acercamiento", mag.t <= tp), ("alejamiento", mag.t >= tp)):
        d = mag[mascara]
        if len(d) >= 500 and d.R.max() / d.R.min() >= 1.2:
            n, a, g = pd_psp.ajuste_por_bins(d.R.values, d.B.values)
            ajustes[tramo] = dict(n=n, a=a, g=g, d=d)

items = [("Distancia mínima", f"{per.loc[enc, 'R'] * pd_psp.UA_EN_RSOL:.2f} R☉", f"{per.loc[enc, 'R']:.4f} UA")]
if mag is not None and len(mag):
    items += [("|B| máximo (1 min)", f"{mag.B.max():,.0f} nT", None),
              ("|B| mediano", f"{mag.B.median():,.1f} nT", f"±{dias} días"),
              ("Cobertura de datos", f"{len(mag) / ((t1 - t0).total_seconds() / 60):.0%}", None)]
kpis(items)
if mag is None or not len(mag):
    st.info(f"Sin datos de campo magnético para este encuentro: CDAWeb los tiene publicados hasta el {fin:%Y-%m-%d}.")

tab_orb, tab_ser, tab_br, tab_ciclo, tab_info = st.tabs(
    ["🛰️ Órbita", "📈 |B|(t)", "📉 |B| vs R", "🔄 Ciclo solar", "ℹ️ Método"])

# ---------------------------------------------------------------- órbita
with tab_orb:
    izq, der = st.columns([3, 2])
    with der:
        dia_rel = st.slider("Posición de la sonda: días desde el perihelio", -dias, dias, 0)
        t_son = tp + pd.Timedelta(days=dia_rel)
        fila = pos.iloc[(pos.t - t_son).abs().argmin()]
        kpis([(f"R el {fila.t:%d-%m-%Y %H:%M} UT", f"{fila.R * pd_psp.UA_EN_RSOL:.1f} R☉", f"{fila.R:.3f} UA")])
        st.caption(
            "Plano de la eclíptica en coordenadas **heliocéntricas inerciales (HGI)**. "
            "En gris, la trayectoria completa de la misión; en azul, la ventana elegida. "
            "Cerca del perihelio la sonda casi **co-rota** con el Sol: recorre ~180° de longitud "
            "en pocos días, algo que se aprecia moviendo el deslizador.")
    with izq:
        fig = go.Figure()
        th = np.linspace(0, 2 * np.pi, 361)
        for nombre, a in (("Mercurio", 0.387), ("Venus", 0.723), ("Tierra", 1.0)):
            fig.add_scatter(x=a * np.cos(th), y=a * np.sin(th), mode="lines", line=dict(color="#9e9e9e", width=1, dash="dot"),
                            name=nombre, hoverinfo="name", showlegend=False)
            fig.add_annotation(x=a * np.cos(np.pi / 4), y=a * np.sin(np.pi / 4), text=nombre, showarrow=False,
                               font=dict(color=GRIS, size=12), yshift=8)
        pas = pos[pos.t <= ahora].iloc[::6]  # 6 h basta para la trayectoria de fondo
        fig.add_scatter(x=pas.x, y=pas.y, mode="lines", line=dict(color="#8c8c8c", width=1), name="Misión", hoverinfo="skip")
        v = pos[(pos.t >= tp - pd.Timedelta(days=dias)) & (pos.t <= tp + pd.Timedelta(days=dias))]
        fig.add_scatter(x=v.x, y=v.y, mode="lines", line=dict(color=AZUL, width=4), name="Ventana",
                        customdata=np.c_[v.t.dt.strftime("%Y-%m-%d %H:%M"), v.R],
                        hovertemplate="%{customdata[0]}<br>R = %{customdata[1]:.3f} UA<extra></extra>")
        fig.add_scatter(x=[0], y=[0], mode="markers", marker=dict(size=18, color="#ffb000", line=dict(color=TINTA, width=1)), name="Sol", hoverinfo="name")
        fig.add_scatter(x=[fila.x], y=[fila.y], mode="markers", marker=dict(size=13, color=ROJO, line=dict(color=TINTA, width=1.5)),
                        name="PSP", hovertemplate=f"PSP · {fila.t:%Y-%m-%d %H:%M}<extra></extra>")
        fig.update_xaxes(range=[-1.1, 1.1], title="x HGI [UA]", zeroline=False)
        fig.update_yaxes(range=[-1.1, 1.1], title="y HGI [UA]", scaleanchor="x", constrain="domain", zeroline=False)
        mostrar(estilo(fig, 620, 380).update_layout(showlegend=False))

# ---------------------------------------------------------------- series de tiempo
with tab_ser:
    if mag is None or not len(mag):
        st.info("No hay datos de campo magnético para este encuentro.")
    else:
        regla = {"1 min": None, "10 min": "10min", "1 h": "1h"}[resol]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.68, 0.32])
        for tramo, aj in ajustes.items():
            m = aj["d"].set_index("t")[["B", "R"]]
            if regla:
                m = m.resample(regla).mean().dropna()
            modelo = 10 ** aj["a"] * m.R ** aj["n"]
            c = TRAMO_COLOR[tramo]
            fig.add_scattergl(x=m.index, y=m.B, mode="lines", line=dict(color=c, width=1.6), legendgroup=tramo,
                              name=f"|B| {tramo}", customdata=np.c_[m.R * pd_psp.UA_EN_RSOL, modelo],
                              hovertemplate="%{x|%Y-%m-%d %H:%M}<br>|B| = %{y:.1f} nT<br>modelo = %{customdata[1]:.1f} nT"
                                            "<br>R = %{customdata[0]:.1f} R☉<extra></extra>", row=1, col=1)
            fig.add_scattergl(x=m.index, y=modelo, mode="lines", line=dict(color=TINTA, width=1.8, dash="dash"),
                              legendgroup="modelo", showlegend=(tramo == "acercamiento"), name="Modelo B₁·R(t)ⁿ",
                              hoverinfo="skip", row=1, col=1)
            fig.add_scattergl(x=m.index, y=m.B / modelo, mode="lines", line=dict(color=c, width=1.3), legendgroup=tramo,
                              showlegend=False, hovertemplate="%{x|%Y-%m-%d %H:%M}<br>|B|/modelo = %{y:.2f}<extra></extra>",
                              row=2, col=1)
        fig.add_hline(y=1, line=dict(color=TINTA, width=1.2), row=2, col=1)
        fig.add_vline(x=tp, line=dict(color=GRIS, dash="dot", width=1.2))
        fig.add_annotation(x=tp, y=1, yref="paper", text="perihelio", showarrow=False, yshift=10,
                           font=dict(color=TINTA, size=11))
        fig.update_yaxes(title="|B| [nT]", type="log", dtick=1, row=1, col=1)
        fig.update_yaxes(title="|B| / modelo", type="log", tickvals=[0.25, 0.5, 1, 2, 4], ticktext=["¼", "½", "1", "2", "4"],
                         row=2, col=1)
        fig.update_xaxes(title="Tiempo (UT)", row=2, col=1)
        mostrar(estilo(fig, 600, 460))
        st.caption(
            f"Es tu ajuste |B| ∝ Rⁿ visto **en el tiempo** (promedios de {resol}). Arriba, |B| medido en el acercamiento "
            "(azul) y el alejamiento (rojo), con el modelo B₁·R(t)ⁿ ajustado en la pestaña *|B| vs R* (negro discontinuo). "
            "Abajo, el cociente |B|/modelo: si la ley de potencias describiera todo, sería 1. Las caídas bruscas "
            "(|B| ≪ modelo) suelen ser cruces de la lámina de corriente heliosférica; los excesos sostenidos, "
            "estructuras como eyecciones de masa coronal o regiones de interacción entre corrientes.")

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
            # Densidad de mediciones con escala de color logarítmica (como LogNorm + 'plasma' del código original)
            lx, ly = np.log10(mag.R.values), np.log10(mag.B.values)
            H, ex, ey = np.histogram2d(lx, ly, bins=(80, 80))
            H = np.where(H > 0, np.log10(H), np.nan).T
            fig.add_heatmap(x=0.5 * (ex[1:] + ex[:-1]), y=0.5 * (ey[1:] + ey[:-1]), z=H, colorscale=PLASMA,
                            showscale=not ES_MOVIL, hoverinfo="skip", name="densidad",
                            colorbar=dict(title=dict(text="N° de<br>mediciones", side="top"), thickness=12, len=0.6,
                                          tickvals=[0, 1, 2, 3], ticktext=["1", "10", "100", "1000"]))
            for tramo, aj in ajustes.items():
                g, n, a, d = aj["g"], aj["n"], aj["a"], aj["d"]
                c = TRAMO_COLOR[tramo]
                xx = np.array([d.R.min(), d.R.max()])
                trazo = "solid" if tramo == "acercamiento" else "dash"
                # halo blanco bajo cada recta para que se lea sobre el mapa de densidad
                fig.add_scatter(x=np.log10(xx), y=a + n * np.log10(xx), mode="lines", legendgroup=tramo, showlegend=False,
                                line=dict(color="white", width=7), hoverinfo="skip")
                fig.add_scatter(x=np.log10(g.R), y=np.log10(g.B), mode="markers", legendgroup=tramo, showlegend=False,
                                marker=dict(size=10, color=c, symbol="diamond" if tramo == "acercamiento" else "circle",
                                            line=dict(color=TINTA, width=1.2)),
                                hovertemplate="R = %{customdata[0]:.3f} UA<br>|B| = %{customdata[1]:.1f} nT<extra></extra>",
                                customdata=np.c_[g.R, g.B])
                fig.add_scatter(x=np.log10(xx), y=a + n * np.log10(xx), mode="lines", legendgroup=tramo,
                                line=dict(color=c, width=3, dash=trazo), name=f"{tramo.capitalize()} (n = {n:.2f})")
            if mostrar_parker:
                rr = np.logspace(np.log10(mag.R.min()), np.log10(mag.R.max()), 50)
                r_ref = np.median(mag.R)
                b_ref = np.median(mag.B[np.isclose(mag.R, r_ref, rtol=0.05)])
                fig.add_scatter(x=np.log10(rr), y=np.log10(pd_psp.parker_B(rr, b_ref, r_ref, V)), mode="lines",
                                line=dict(color=TINTA, dash="dot", width=2.5), name=f"Parker ({V} km/s)")
            ticks_R = [0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.5]
            ticks_B = [1, 3, 10, 30, 100, 300, 1000, 3000]
            fig.update_xaxes(title="Distancia al Sol R [UA]", tickvals=np.log10(ticks_R), ticktext=ticks_R)
            fig.update_yaxes(title="|B| [nT]", tickvals=np.log10(ticks_B), ticktext=ticks_B)
            mostrar(estilo(fig, 560, 420))
        with der:
            kpis([(f"n ({tramo})", f"{aj['n']:.2f}", f"|B|(1 UA) ≈ {10 ** aj['a']:.1f} nT") for tramo, aj in ajustes.items()])
            st.caption("Color: número de mediciones de 1 min por celda (escala logarítmica). Rombos azules y círculos rojos: "
                       "medianas por bin de log R del acercamiento y del alejamiento; recta continua y discontinua: sus "
                       "ajustes; punteada: espiral de Parker. Para ventanas cortas el rango en R es pequeño y la "
                       "pendiente es poco confiable; use 30–40 días para comparar con la pestaña *Ciclo solar*.")

# ---------------------------------------------------------------- ciclo solar
with tab_ciclo:
    with st.expander("¿Cómo leer estos gráficos?", expanded=not ES_MOVIL):
        st.markdown("""
Cada punto resume **un tramo de 40 días** de un encuentro: el **acercamiento** (rombos azules, 40 días antes del perihelio)
o el **alejamiento** (círculos rojos, 40 días después). En cada tramo se ajusta una ley de potencias
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
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.075, subplot_titles=(
        "1 · Índice n de la ley |B| ∝ Rⁿ", "2 · |B| extrapolado a 1 UA", "3 · Proxy de flujo abierto |B_R| r²",
        "4 · Número de manchas solares (actividad)"))
    fig.update_annotations(font=dict(size=12 if ES_MOVIL else 13, color=TINTA), x=0, xanchor="left", yshift=8)
    for tramo, d in res.groupby("tramo"):
        c = TRAMO_COLOR[tramo]
        comun = dict(mode="markers", marker=dict(size=9, color=c, symbol="diamond" if tramo == "acercamiento" else "circle",
                                                 line=dict(color="white", width=1)),
                     legendgroup=tramo, customdata=d.encuentro)
        fig.add_scatter(x=d.anio, y=d.n, error_y=dict(array=d.dn, color=c, thickness=1.5, width=0), name=tramo.capitalize(),
                        hovertemplate="E%{customdata}: n = %{y:.2f}<extra></extra>", row=1, col=1, **comun)
        b1 = 10**d.log10_B_1UA
        fig.add_scatter(x=d.anio, y=b1, error_y=dict(array=np.log(10) * b1 * d.dlog10_B_1UA, color=c, thickness=1.5, width=0),
                        showlegend=False, hovertemplate="E%{customdata}: %{y:.2f} nT<extra></extra>", row=2, col=1, **comun)
    f = res.groupby(["encuentro", "anio"], as_index=False).BR_r2_nT_UA2.mean()
    fig.add_scatter(x=f.anio, y=f.BR_r2_nT_UA2, mode="lines+markers", line=dict(color=TINTA, width=2), marker=dict(size=8),
                    name="|B_R| r²", customdata=f.encuentro, hovertemplate="E%{customdata}: %{y:.2f} nT UA²<extra></extra>",
                    row=3, col=1)
    fig.add_scatter(x=man.anio_decimal, y=man.manchas, mode="lines", line=dict(color="#7a5c00", width=2),
                    name="Manchas (SILSO)", hovertemplate="%{y:.0f}<extra></extra>", row=4, col=1)
    fig.add_hline(y=-2, line=dict(color=TINTA, dash="dash", width=1.2), row=1, col=1)
    sel = res[res.encuentro == enc]
    if len(sel):
        fig.add_vline(x=sel.anio.iloc[0], line=dict(color=GRIS, width=1.5, dash="dot"))
    fig.update_yaxes(title="n en |B| ∝ Rⁿ", row=1, col=1)
    fig.update_yaxes(title="|B| a 1 UA [nT]", row=2, col=1)
    fig.update_yaxes(title="|B_R| r² [nT UA²]", row=3, col=1)
    fig.update_yaxes(title="Nº manchas", row=4, col=1)
    fig.update_xaxes(title="Año", row=4, col=1)
    estilo(fig, 950, 860).update_layout(margin=dict(t=90 if not ES_MOVIL else 100), legend=dict(y=1.07 if not ES_MOVIL else 1.09))
    mostrar(fig)
    st.caption("Resultados precalculados con `Codigo Propuesto/analisis_encuentros.py` (ventanas de ±40 días, "
               "barras de error por bootstrap de bloques diarios). La línea punteada gris marca el encuentro elegido. "
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

st.divider()
st.caption("Datos: NASA/CDAWeb vía HAPI · FIELDS (Bale et al. 2016) · SILSO. "
           "Código: rama `revision-2026` de mumioladev/investigacion-ssp-.")
