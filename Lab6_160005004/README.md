# Laboratorio 6 — Análisis de datos de entrada y bondad de ajuste

Santiago Barrera Meza · 160005004 · Simulación Computacional, Universidad de los Llanos

| Archivo | Contenido |
|---|---|
| `Informe_Lab6_160005004.pdf` | Informe final (copia del PDF compilado en `informe/`) |
| `Lab6_160005004_analisis_entrada.ipynb` | Puntos 5.1 y 5.2: estadística descriptiva, histogramas y gráficas de independencia y estabilidad |
| `Lab6_160005004_ajuste_curvas.ipynb` | Punto 5.3: ajuste de 9 distribuciones con SSE, AIC, BIC y KS; tres mejores por conjunto |
| `datos/` | `dataset-A.txt` … `dataset-D.txt`, descargados de los enlaces de la guía |
| `figuras/`, `resultados/` | Gráficas PNG y tablas CSV generadas por los cuadernos |
| `informe/` | Fuente LaTeX (IEEEtran) y tablas `.tex` generadas |
| `build_lab6.py`, `tablas_latex.py` | Generan y ejecutan los cuadernos y convierten los CSV en tablas LaTeX |

## Reproducir

```
pip install numpy scipy pandas matplotlib statsmodels nbformat nbclient ipykernel
python build_lab6.py      # crea y ejecuta los dos cuadernos
python tablas_latex.py    # regenera informe/tablas/*.tex
cd informe && pdflatex Informe_Lab6_160005004.tex && pdflatex Informe_Lab6_160005004.tex
```

En Colab basta con abrir cada cuaderno y subir la carpeta `datos/` junto a él.

## Resultado en una línea por conjunto

- **A:** estacionario pero correlacionado (r1 = 0.49). Mejor marginal: normal(0.195, 0.0437).
- **B:** compatible con IID. Weibull(c = 0.91, β = 0.196), prácticamente exponencial de media 0.205.
- **C:** no estacionario (la media de la 2.ª mitad es 2.65 veces la de la 1.ª). Gamma(α = 0.706, β = 1080) solo como marginal.
- **D:** compatible con IID. Lognormal(μ = 0.241, σ = 1.019).
