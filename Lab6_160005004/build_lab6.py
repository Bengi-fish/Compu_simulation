"""Genera y ejecuta los dos cuadernos del laboratorio 6.

Uso: python build_lab6.py   (desde cualquier carpeta; usa rutas relativas a este archivo)
Produce:
  Lab6_160005004_analisis_entrada.ipynb  (puntos 5.1 y 5.2)
  Lab6_160005004_ajuste_curvas.ipynb     (punto 5.3)
  figuras/*.png, resultados/*.csv, informe/tablas/*.tex
"""
from pathlib import Path
import textwrap
import nbformat
from nbclient import NotebookClient

BASE = Path(__file__).resolve().parent


def md(cells, s):
    cells.append(nbformat.v4.new_markdown_cell(textwrap.dedent(s).strip()))


def code(cells, s):
    cells.append(nbformat.v4.new_code_cell(textwrap.dedent(s).strip()))


ENCABEZADO = '''
**Santiago Barrera Meza · 160005004**
Simulación Computacional · Universidad de los Llanos · Guía FO-DOC-112, laboratorio 6

Los datos `dataset-A.txt` … `dataset-D.txt` se descargaron de los enlaces de la guía y están en
la carpeta `datos/`. En Colab, subir esa carpeta (o los cuatro archivos) junto al cuaderno.
'''

CARGA = '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATOS = Path('datos')
FIGURAS = Path('figuras'); FIGURAS.mkdir(exist_ok=True)
RESULTADOS = Path('resultados'); RESULTADOS.mkdir(exist_ok=True)

NOMBRES = ['A', 'B', 'C', 'D']
datos = {k: np.loadtxt(DATOS / f'dataset-{k}.txt') for k in NOMBRES}
for k, x in datos.items():
    print(f'Dataset {k}: {len(x)} observaciones, primeras 5 = {np.round(x[:5], 4)}')
'''

# ----------------------------------------------------------------------------
# Cuaderno 1: estadística descriptiva y análisis de datos de entrada
# ----------------------------------------------------------------------------
c1 = []
md(c1, '# Laboratorio 6 — Análisis de datos de entrada (puntos 5.1 y 5.2)\n' + ENCABEZADO)
md(c1, '## Librerías y carga de datos')
code(c1, CARGA + '''
from statsmodels.graphics import tsaplots
from statsmodels.tsa.stattools import acf
from scipy import stats
''')

md(c1, '''
## 5.1 Estadística descriptiva
Varianza y desviación estándar muestrales (denominador $n-1$). Los percentiles usan la
interpolación lineal por defecto de NumPy. Se agregan asimetría y curtosis (exceso) porque
ayudan a elegir las distribuciones candidatas.
''')
code(c1, '''
def descriptiva(x):
    return {
        'Tamaño de la muestra': len(x),
        'Mínimo': np.min(x),
        'Máximo': np.max(x),
        'Media': np.mean(x),
        'Varianza': np.var(x, ddof=1),
        'Desviación estándar': np.std(x, ddof=1),
        'Percentil 25% (Q1)': np.percentile(x, 25),
        'Percentil 50% (Q2 o mediana)': np.percentile(x, 50),
        'Percentil 75% (Q3)': np.percentile(x, 75),
        'Coef. de variación': np.std(x, ddof=1) / np.mean(x),
        'Asimetría': stats.skew(x, bias=False),
        'Curtosis (exceso)': stats.kurtosis(x, bias=False),
    }

tabla1 = pd.DataFrame({f'Dataset {k}': descriptiva(x) for k, x in datos.items()})
tabla1.to_csv(RESULTADOS / 'tabla1_descriptiva.csv')
pd.options.display.float_format = '{:.6g}'.format
tabla1
''')

md(c1, '### Histogramas con 20 particiones')
code(c1, '''
fig, axs = plt.subplots(2, 2, figsize=(11, 8))
for ax, (k, x) in zip(axs.flat, datos.items()):
    ax.hist(x, bins=20, color='#1f4fbf', edgecolor='white')
    ax.set_title(f'Dataset {k}', loc='left', fontweight='bold')
    ax.set_xlabel('x'); ax.set_ylabel('Frecuencia')
    ax.grid(axis='y', alpha=0.3)
fig.tight_layout(); fig.savefig(FIGURAS / 'histogramas.png', dpi=160); plt.show()
''')

md(c1, '''
## 5.2 Análisis de datos de entrada
Funciones adaptadas del cuaderno de clase *Example. Input Data Analysis.ipynb*. Cada función
dibuja sobre un eje para poner los cuatro conjuntos en una sola figura. Cambios respecto al
original:

* **Conteo de llegadas:** el original guarda el conteo del intervalo $k$ en `counts[k-1]`, lo que
  corre todas las barras una posición y deja el primer intervalo en la última. Aquí cada conteo va
  en su propio índice y los intervalos se definen como $[t_k, t_{k+1})$ para no perder llegadas
  que caen justo en un borde.
* **Media móvil:** se conserva la ventana del original (`window`, con $W$ = `window/2` a cada
  lado). Con 200 datos se usa `window = 40` ($W = 20$), porque `window = 100` del ejemplo (pensado
  para unos 1000 datos) promediaría la mitad de la muestra en cada punto.
* El horizonte $T$ de cada conjunto es la suma de sus valores (instante de la última llegada).

Los cuatro conjuntos se tratan como tiempos entre llegadas, igual que en el ejemplo de clase.
''')
code(c1, '''
def plot_lag(ax, x, k):
    tsaplots.plot_acf(x, lags=20, zero=False, ax=ax, title=f'Dataset {k}')
    ax.set_xlabel('Retraso k'); ax.set_ylabel('Correlación')
    ax.set_yticks(np.arange(-1, 1.25, 0.25)); ax.set_xticks(np.arange(1, 21, 1))
    ax.set_xlim(0.5, 20.5); ax.set_ylim(-1, 1)

def plot_scatter(ax, x, k):
    ax.scatter(x[:-1], x[1:], marker='^', s=14)
    ax.grid(alpha=0.4)
    ax.set_xlim(x.min(), x.max()); ax.set_ylim(x.min(), x.max())
    ax.set_title(f'Dataset {k}'); ax.set_xlabel('Observación [k]'); ax.set_ylabel('Observación [k+1]')

def plot_patron_llegadas(ax, x, k):
    llegadas = np.cumsum(x)
    proporcion = np.arange(1, len(x) + 1) / len(x)
    ax.plot(llegadas, proporcion, 'b')
    ax.plot([0, llegadas[-1]], [0, 1], 'k--', lw=0.8, label='Tasa constante')
    ax.set_title(f'Dataset {k}'); ax.set_xlabel('Tiempo T'); ax.set_ylabel('Proporción antes de T')
    ax.legend(loc='lower right', fontsize=8)

def conteos_intervalos(x, nbins=40):
    llegadas = np.cumsum(x)
    T = llegadas[-1]
    bordes = np.linspace(0, T, nbins + 1)
    conteos, _ = np.histogram(llegadas, bins=bordes)
    return conteos, T / nbins, T

def plot_conteos(ax, x, k, nbins=40):
    conteos, ancho, T = conteos_intervalos(x, nbins)
    ax.bar(range(1, nbins + 1), conteos, width=1, edgecolor='black', color='white')
    ax.axhline(len(x) / nbins, color='red', lw=0.8, ls='--')
    ax.set_title(f'Dataset {k}: {nbins} intervalos de ancho {ancho:.4g} entre 0 y {T:.4g}', fontsize=9)
    ax.set_xlabel('Intervalo'); ax.set_ylabel('Conteo')

def media_movil(x, window=40):
    mid = round(window / 2)
    n = len(x)
    return np.array([np.mean(x[max(0, i - mid): min(n, i + mid + 1)]) for i in range(n)])

def plot_media_movil(ax, x, k, window=40):
    y = media_movil(x, window)
    m, s = np.mean(y), np.std(y)
    ax.plot(y)
    ax.axhline(m, color='black'); ax.axhline(m + 3 * s, color='green'); ax.axhline(m - 3 * s, color='green')
    ax.set_ylim(m - 9 * s, m + 9 * s); ax.set_xlim(0, len(y))
    ax.set_title(f'Dataset {k}: media móvil, ventana {window}')
    ax.set_xlabel('Posición'); ax.set_ylabel('Media móvil')

def plot_secuencia(ax, x, k):
    ax.plot(x, 'r.', ms=4)
    ax.set_title(f'Dataset {k}'); ax.set_xlabel('Orden de la observación'); ax.set_ylabel('Valor $x_i$')

def figura(fn, archivo, titulo):
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for ax, (k, x) in zip(axs.flat, datos.items()):
        fn(ax, x, k)
    fig.suptitle(titulo, fontweight='bold')
    fig.tight_layout(); fig.savefig(FIGURAS / archivo, dpi=160); plt.show()
''')

md(c1, '### Secuencia de valores en orden de ocurrencia')
code(c1, "figura(plot_secuencia, 'secuencia.png', 'Valores en orden de ocurrencia')")
md(c1, '### a. Correlaciones de retraso estimadas (*Estimated lag correlations*)')
code(c1, "figura(plot_lag, 'correlaciones.png', 'Correlaciones de retraso estimadas (k = 1 a 20)')")
md(c1, '### b. Diagrama de dispersión (*Scatter diagram*)')
code(c1, "figura(plot_scatter, 'dispersion.png', 'Diagramas de dispersión de pares consecutivos')")
md(c1, '### c. Patrón de hora de llegada (*Arrival time pattern*)')
code(c1, "figura(plot_patron_llegadas, 'patron_llegadas.png', 'Patrón de hora de llegada')")
md(c1, '### d. Conteo de llegadas vs intervalos (*Arrival counts vs intervals*)')
code(c1, "figura(plot_conteos, 'conteos.png', 'Conteo de llegadas en 40 intervalos')")
md(c1, '### e. Gráfico de media móvil (*Moving average plot*)')
code(c1, "figura(plot_media_movil, 'media_movil.png', 'Gráficos de media móvil (ventana 40)')")

md(c1, '''
### Resumen numérico de independencia y estabilidad
Las gráficas son el criterio principal, como recomienda el material de clase. Esta tabla solo
cuantifica lo que muestran: las correlaciones de retraso 1 a 3 frente a la banda aproximada
$\\pm 2/\\sqrt{n}$, cuántos de los retrasos 1 a 10 salen de esa banda, y la media de cada mitad y
cada cuarto de la muestra. El cociente de medias compara la segunda mitad con la primera.
''')
code(c1, '''
n = 200
banda = 2 / np.sqrt(n)
filas = {}
for k, x in datos.items():
    r = acf(x, nlags=10)[1:]
    cuartos = [q.mean() for q in np.array_split(x, 4)]
    filas[f'Dataset {k}'] = {
        'r1': r[0], 'r2': r[1], 'r3': r[2],
        'Retrasos 1-10 fuera de banda': int(np.sum(np.abs(r) > banda)),
        'Media 1.a mitad': x[:100].mean(), 'Media 2.a mitad': x[100:].mean(),
        'Cociente de medias': x[100:].mean() / x[:100].mean(),
        'Media por cuartos': ' / '.join(f'{c:.4g}' for c in cuartos),
    }
tabla_iid = pd.DataFrame(filas)
tabla_iid.to_csv(RESULTADOS / 'tabla_independencia.csv')
print(f'Banda aproximada ±2/sqrt(n) = ±{banda:.3f}')
tabla_iid
''')

# ----------------------------------------------------------------------------
# Cuaderno 2: ajuste de curvas
# ----------------------------------------------------------------------------
c2 = []
md(c2, '# Laboratorio 6 — Ajuste de curvas y bondad de ajuste (punto 5.3)\n' + ENCABEZADO)
md(c2, '## Librerías y carga de datos')
code(c2, CARGA + '''
import warnings
from scipy import stats
warnings.filterwarnings('ignore', category=RuntimeWarning)
''')

md(c2, '''
## Distribuciones candidatas
Las cinco de la guía (exponencial, lognormal, normal, gamma y beta) y cuatro adicionales:
**Weibull**, **log-logística** (`fisk` en SciPy), **gaussiana inversa** y **Pareto
generalizada**. Se eligieron para cubrir colas ligeras (Weibull), intermedias (gaussiana
inversa) y pesadas (log-logística y Pareto generalizada), porque los conjuntos tienen
asimetrías entre −0.3 y 3.2.

Criterios de ajuste, siguiendo [Amat2021]:

* Los parámetros se estiman por máxima verosimilitud con `scipy.stats.<dist>.fit`.
* Todos los datos son positivos, así que las distribuciones de soporte $[0,\\infty)$ se ajustan con
  localización fija en 0 (`floc=0`). La normal conserva sus dos parámetros.
* La beta necesita un soporte acotado $[a,b]$. Se fija
  $a = \\min(x) - \\frac{\\max(x)-\\min(x)}{n-1}$ y $b = \\max(x) + \\frac{\\max(x)-\\min(x)}{n-1}$
  (una separación media más allá de cada extremo) y se estiman los dos parámetros de forma.
  Como $a$ y $b$ salen de los datos, para AIC y BIC se cuentan cuatro parámetros.
* $k$ = número de parámetros estimados; $\\ln L=\\sum_i \\ln f(x_i;\\hat\\theta)$.
* $\\mathrm{AIC} = 2k - 2\\ln L$, $\\mathrm{BIC} = k\\ln n - 2\\ln L$.
* $\\mathrm{SSE} = \\sum_j \\big(h_j - f(c_j;\\hat\\theta)\\big)^2$, con $h_j$ la densidad del
  histograma de 20 particiones y $c_j$ el centro de cada partición. El SSE depende de las
  particiones y de la escala de los datos, así que solo compara distribuciones dentro de un mismo
  conjunto.
* Como control adicional se reporta el estadístico de Kolmogórov-Smirnov $D$. Su valor p no es
  exacto cuando los parámetros se estiman con los mismos datos, por eso solo se usa $D$.

El orden final se hace por AIC; BIC y SSE se revisan para ver si cambian la elección.
''')
code(c2, '''
CANDIDATAS = {
    'Exponencial':          (stats.expon,       {'floc': 0}),
    'Lognormal':            (stats.lognorm,     {'floc': 0}),
    'Normal':               (stats.norm,        {}),
    'Gamma':                (stats.gamma,       {'floc': 0}),
    'Beta':                 (stats.beta,        None),   # soporte fijado aparte
    'Weibull':              (stats.weibull_min, {'floc': 0}),
    'Log-logística':        (stats.fisk,        {'floc': 0}),
    'Gaussiana inversa':    (stats.invgauss,    {'floc': 0}),
    'Pareto generalizada':  (stats.genpareto,   {'floc': 0}),
}
NOMBRES_PARAM = {
    'Exponencial': ['loc', 'scale'], 'Normal': ['mu', 'sigma'],
    'Lognormal': ['s', 'loc', 'scale'], 'Gamma': ['a', 'loc', 'scale'],
    'Beta': ['a', 'b', 'loc', 'scale'], 'Weibull': ['c', 'loc', 'scale'],
    'Log-logística': ['c', 'loc', 'scale'], 'Gaussiana inversa': ['mu', 'loc', 'scale'],
    'Pareto generalizada': ['c', 'loc', 'scale'],
}

def ajustar(x, nombre, bins=20):
    dist, fijos = CANDIDATAS[nombre]
    n = len(x)
    if nombre == 'Beta':
        margen = (x.max() - x.min()) / (n - 1)
        a, b = x.min() - margen, x.max() + margen
        params = dist.fit(x, floc=a, fscale=b - a)
        k = 4
    else:
        params = dist.fit(x, **fijos)
        k = len(params) - len(fijos)
    logL = np.sum(dist.logpdf(x, *params))
    densidad, bordes = np.histogram(x, bins=bins, density=True)
    centros = (bordes[:-1] + bordes[1:]) / 2
    sse = np.sum((densidad - dist.pdf(centros, *params)) ** 2)
    D = stats.kstest(x, dist.cdf, args=params).statistic
    return {
        'Distribución': nombre, 'k': k,
        'Parámetros': ', '.join(f'{p}={v:.4g}' for p, v in zip(NOMBRES_PARAM[nombre], params)),
        'params': params, 'lnL': logL, 'SSE': sse,
        'AIC': 2 * k - 2 * logL, 'BIC': k * np.log(n) - 2 * logL, 'KS D': D,
    }

def tabla_ajuste(x):
    t = pd.DataFrame([ajustar(x, nombre) for nombre in CANDIDATAS])
    t['Orden AIC'] = t['AIC'].rank().astype(int)
    t['Orden BIC'] = t['BIC'].rank().astype(int)
    t['Orden SSE'] = t['SSE'].rank().astype(int)
    return t

pd.options.display.float_format = '{:.5g}'.format
pd.options.display.max_colwidth = 60
COLUMNAS = ['Distribución', 'Parámetros', 'SSE', 'AIC', 'BIC', 'KS D', 'Orden AIC', 'Orden BIC', 'Orden SSE']
ajustes = {}
''')

for k in 'ABCD':
    md(c2, f'## Dataset {k}')
    code(c2, f'''
ajustes['{k}'] = tabla_ajuste(datos['{k}'])
ajustes['{k}'].drop(columns='params').to_csv(RESULTADOS / 'ajuste_dataset_{k}.csv', index=False)
ajustes['{k}'][COLUMNAS]
''')

md(c2, '''
## Tres mejores distribuciones por conjunto
Se ordenan por AIC. La figura superpone sobre el histograma (densidad, 20 particiones) la
densidad de las tres primeras.
''')
code(c2, '''
COLORES = ['#d62728', '#2ca02c', '#000000']
ESTILOS = ['-', '--', ':']

def top3(k):
    return ajustes[k].sort_values('AIC').head(3)

def plot_top3(ax, k):
    x = datos[k]
    alturas, _, _ = ax.hist(x, bins=20, density=True, color='#1f4fbf', alpha=0.35, edgecolor='white', label='Datos')
    malla = np.linspace(max(x.min() - 0.05 * np.ptp(x), 1e-9 if x.min() > 0 else x.min()), x.max(), 600)
    for (_, fila), color, estilo in zip(top3(k).iterrows(), COLORES, ESTILOS):
        dist = CANDIDATAS[fila['Distribución']][0]
        ax.plot(malla, dist.pdf(malla, *fila['params']), color=color, ls=estilo, lw=1.8,
                label=f"{fila['Distribución']} (AIC {fila['AIC']:.1f})")
    ax.set_title(f'Dataset {k}', loc='left', fontweight='bold')
    # Las densidades con forma < 1 tienden a infinito en 0; se recorta el eje para ver el histograma
    ax.set_ylim(0, 1.3 * alturas.max())
    ax.set_xlabel('x'); ax.set_ylabel('Densidad'); ax.legend(fontsize=8)

for k in NOMBRES:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    plot_top3(ax, k)
    fig.tight_layout(); fig.savefig(FIGURAS / f'top3_dataset_{k}.png', dpi=160); plt.show()

fig, axs = plt.subplots(2, 2, figsize=(12, 8.5))
for ax, k in zip(axs.flat, NOMBRES):
    plot_top3(ax, k)
fig.tight_layout(); fig.savefig(FIGURAS / 'top3_todos.png', dpi=160); plt.close(fig)

resumen = pd.concat({f'Dataset {k}': top3(k)[['Distribución', 'Parámetros', 'SSE', 'AIC', 'BIC', 'KS D']]
                     .reset_index(drop=True) for k in NOMBRES})
resumen.to_csv(RESULTADOS / 'top3.csv')
resumen
''')

md(c2, '''
### Gráficas Q-Q de la mejor distribución
Complementan el histograma: si el modelo es bueno, los puntos siguen la diagonal, también en
las colas.
''')
code(c2, '''
fig, axs = plt.subplots(2, 2, figsize=(10, 8))
for ax, k in zip(axs.flat, NOMBRES):
    x = np.sort(datos[k]); n = len(x)
    mejor = top3(k).iloc[0]
    dist = CANDIDATAS[mejor['Distribución']][0]
    teoricos = dist.ppf((np.arange(1, n + 1) - 0.5) / n, *mejor['params'])
    ax.plot(teoricos, x, 'o', ms=3)
    lim = [min(teoricos.min(), x.min()), max(teoricos.max(), x.max())]
    ax.plot(lim, lim, 'r-', lw=1)
    ax.set_title(f"Dataset {k}: {mejor['Distribución']}")
    ax.set_xlabel('Cuantil teórico'); ax.set_ylabel('Cuantil observado')
fig.tight_layout(); fig.savefig(FIGURAS / 'qq_mejor.png', dpi=160); plt.show()
''')

md(c2, '''
### Dataset C por mitades
El análisis del punto 5.2 indica que C no es estacionario: la media de la segunda mitad casi
triplica la de la primera. Ajustar una sola distribución a los 200 datos mezcla dos regímenes.
Como verificación se repite el ajuste en cada mitad.
''')
code(c2, '''
mitades = {}
for nombre, x in [('C primera mitad', datos['C'][:100]), ('C segunda mitad', datos['C'][100:])]:
    t = tabla_ajuste(x)
    mitades[nombre] = t.sort_values('AIC').head(3)[['Distribución', 'Parámetros', 'AIC', 'BIC', 'KS D']].reset_index(drop=True)
    print(nombre, f'media = {x.mean():.4g}')
tabla_mitades = pd.concat(mitades)
tabla_mitades.to_csv(RESULTADOS / 'top3_C_mitades.csv')
tabla_mitades
''')


def ejecutar(cells, nombre):
    nb = nbformat.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.12'}})
    NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': str(BASE)}}).execute()
    nbformat.validate(nb)
    nbformat.write(nb, BASE / nombre)
    print('Ejecutado', nombre)


if __name__ == '__main__':
    ejecutar(c1, 'Lab6_160005004_analisis_entrada.ipynb')
    ejecutar(c2, 'Lab6_160005004_ajuste_curvas.ipynb')
