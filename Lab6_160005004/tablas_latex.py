"""Convierte los CSV de resultados/ en tablas LaTeX para el informe (informe/tablas/*.tex)."""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
RES = BASE / 'resultados'
OUT = BASE / 'informe' / 'tablas'
OUT.mkdir(parents=True, exist_ok=True)


def num(v, cifras=4):
    """Formato con cifras significativas; notación científica en LaTeX si hace falta."""
    s = f'{v:.{cifras}g}'
    if 'e' in s:
        m, e = s.split('e')
        return f'${m}\\times10^{{{int(e)}}}$'
    return s


def params_tex(p, dist):
    # Quita la localización fija en 0 y pasa los nombres a símbolos
    valores = dict(par.split('=') for par in p.split(', '))
    valores = {k: float(v) for k, v in valores.items()}
    if dist == 'Beta':
        lo, hi = valores['loc'], valores['loc'] + valores['scale']
        return (f"$\\alpha_1={num(valores['a'])}$, $\\alpha_2={num(valores['b'])}$, "
                f"$[{num(lo, 3).strip('$')},\\,{num(hi, 3).strip('$')}]$")
    simbolos = {'s': '\\sigma', 'scale': '\\beta', 'mu': '\\mu', 'sigma': '\\sigma', 'a': '\\alpha',
                'c': '\\xi' if dist == 'Pareto generalizada' else 'c'}
    partes = [f'${simbolos[k]}={num(v).strip("$")}$' for k, v in valores.items() if k != 'loc']
    return ', '.join(partes)


# Tabla 1: descriptiva
t1 = pd.read_csv(RES / 'tabla1_descriptiva.csv', index_col=0)
filas = []
for medida, fila in t1.iterrows():
    medida_tex = medida.replace('%', '\\,\\%')
    if medida == 'Tamaño de la muestra':
        vals = [f'{int(v)}' for v in fila]
    else:
        vals = [num(v) for v in fila]
    filas.append(f'{medida_tex} & ' + ' & '.join(vals) + ' \\\\')
(OUT / 'descriptiva.tex').write_text('\n'.join(filas) + '\n', encoding='utf-8')

# Tabla de independencia
ti = pd.read_csv(RES / 'tabla_independencia.csv', index_col=0)
etiquetas = {'r1': '$r_1$', 'r2': '$r_2$', 'r3': '$r_3$',
             'Retrasos 1-10 fuera de banda': 'Retrasos 1--10 fuera de $\\pm2/\\sqrt{n}$',
             'Media 1.a mitad': 'Media 1.ª mitad', 'Media 2.a mitad': 'Media 2.ª mitad',
             'Cociente de medias': 'Cociente 2.ª/1.ª mitad'}
filas = []
for medida, fila in ti.iterrows():
    if medida == 'Media por cuartos':
        continue
    if medida.startswith('Retrasos'):
        vals = [str(int(float(v))) for v in fila]
    elif medida.startswith('r'):
        vals = [f'{float(v):.3f}' for v in fila]
    else:
        vals = [num(float(v)) for v in fila]
    filas.append(f'{etiquetas[medida]} & ' + ' & '.join(vals) + ' \\\\')
(OUT / 'independencia.tex').write_text('\n'.join(filas) + '\n', encoding='utf-8')

# Tablas de ajuste por conjunto (orden de la guía)
for k in 'ABCD':
    t = pd.read_csv(RES / f'ajuste_dataset_{k}.csv')
    filas = []
    for _, f in t.iterrows():
        marca = f"\\textbf{{{f['Distribución']}}}" if f['Orden AIC'] <= 3 else f['Distribución']
        filas.append(f"{marca} & {params_tex(f['Parámetros'], f['Distribución'])} & {num(f['SSE'], 3)} & "
                     f"{f['AIC']:.2f} & {f['BIC']:.2f} & {f['KS D']:.3f} \\\\")
    (OUT / f'ajuste_{k}.tex').write_text('\n'.join(filas) + '\n', encoding='utf-8')

print('Tablas escritas en', OUT)
