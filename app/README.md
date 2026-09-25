# Explorador PSP (prototipo Streamlit)

App web para explorar el campo magnético de Parker Solar Probe por encuentro.
Los datos se descargan en vivo desde CDAWeb (API HAPI); los resultados del ciclo solar
vienen precalculados en `datos/resultados_por_encuentro.csv` (generado con
`../Codigo Propuesto/analisis_encuentros.py`).

## Pestañas
- **Órbita**: trayectoria en el plano de la eclíptica (HGI), con la ventana del encuentro y la posición de la sonda.
- **|B|(t)**: magnitud del campo alrededor del perihelio (la distancia R aparece al pasar el cursor o tocar la curva).
- **|B| vs R**: ajuste |B| ∝ Rⁿ (acercamiento y alejamiento) y espiral de Parker de referencia.
- **Ciclo solar**: n, |B| a 1 UA y |B_R| r² para los 27 encuentros, junto al número de manchas.
- **Método y fuentes**.

## Uso en teléfonos
Los controles están en el área principal (no en la barra lateral, que en móvil queda oculta).
La app detecta teléfonos por el *User-Agent*: reduce la altura de los gráficos, oculta la barra de
herramientas de Plotly y desactiva el zoom por arrastre para que deslizar el dedo desplace la página.

## Ejecutar localmente
```bash
cd app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Publicar gratis en Streamlit Community Cloud
1. Entrar a https://share.streamlit.io con la cuenta de GitHub.
2. *Create app* → repositorio `mumioladev/investigacion-ssp-`, rama `revision-2026`,
   archivo principal `app/streamlit_app.py`.
3. Deploy. La URL queda del tipo `https://<nombre>.streamlit.app`.

Streamlit Cloud instala las dependencias desde `app/requirements.txt`.

## Actualizar los resultados del ciclo solar
```bash
cd "Codigo Propuesto"
python analisis_encuentros.py
cp resultados_por_encuentro.csv ../app/datos/
```
