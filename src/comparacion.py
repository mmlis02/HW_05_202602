"""Comparación de los dos caminos de extracción (reglas y LLM) sobre los mismos textos.

La usan 03_extraccion (sobre las referencias) y 06_resultados (sobre el audio real). No extrae nada: recibe
lo que devolvieron src.extraccion_reglas.extraer y src.extraccion_llm.extraer.

- registro(extraidos, textos): una fila por clip y campo con el valor, si acierta contra el ground truth, el
  estado de verificación (src.verificacion, la misma para los dos caminos) y el error, si lo hubo.
- trampas(por_camino): cómo resuelve cada camino las trampas del ground truth (TRAMPAS).
- fuera_del_glosario(extraidos, textos): las tecnologías que no están en asr.glosario.tecnologias, con su
  estado de verificación. Las reglas solo pueden encontrar términos del glosario; el LLM no tiene esa lista.
- evidencia_literal(extraidos, textos): si cada evidencia está en la transcripción, tal cual o después de
  normalizar las dos.
- gt_en_texto(clip, texto): si el valor verdadero de cada campo aparece literalmente en el texto, con la misma
  regla de verificación. Separa una corrección del ASR (el valor está en la referencia y no en el audio)
  de una interpretación (no está en ninguno de los dos, como los 2.5 años de E4).
"""

from functools import cache

import pandas as pd

from src.config import cargar_config
from src.metricas import aciertos, ground_truth
from src.normalizacion import normalizar_texto
from src.verificacion import verificar

# Las trampas del ground truth (columnas trampas y correccion_cliente) que dependen de un campo extraído.
TRAMPAS = [
    ("e1", '"casi cinco" antes de "cuatro años y medio"', "anios_experiencia"),
    ("e1", "sueldo actual (5800) antes de la pretensión", "pretension_salarial"),
    ("e2", 'años dichos como "desde dos mil veintitrés"', "anios_experiencia"),
    ("e2", "moneda en dólares", "pretension_salarial"),
    ("e3", "Nagios: tecnología abandonada", "tecnologias"),
    ("e3", 'rango "entre nueve y diez mil" con ideal 9500', "pretension_salarial"),
    ("e4", "los 2.5 años nunca se dicen: correcto, pero debe quedar sin_verificar", "anios_experiencia"),
    ("e4", "autocorrección 4200 → 4800", "pretension_salarial"),
    ("e5", "sueldo actual (6200) antes de la pretensión", "pretension_salarial"),
    ("e5", "Selenium antiguo pero todavía en uso", "tecnologias"),
    ("l1", "autocorrección: 1 jarra → 2 jarras", "items"),
    ("l2", "autocorrección: 2 medios pollos → 1 entero", "items"),
    ("l3", "autocorrección: dirección 1043 → 1034", "direccion_entrega"),
    ("l4", "autocorrección: 2 mollejitas → 1, y agrega anticuchos", "items"),
    ("l5", "autocorrección: 2 enteros → 1 entero + 1 medio", "items"),
]


def registro(extraidos: dict, textos: dict) -> pd.DataFrame:
    """Una fila por clip y campo: valor, acierta, estado de verificación y error.

    Args:
        extraidos: {clip: salida de extraer()}.
        textos: {clip: transcripción de la que salió}.
    """
    gt = _gt()
    filas = []
    for clip, campos in extraidos.items():
        esquema = _esquema(clip)
        acierta = aciertos({k: v["valor"] for k, v in campos.items()}, gt[clip], esquema)
        estados = verificar(campos, textos[clip])
        filas += [{"clip": clip, "campo": campo, "valor": dato["valor"], "ground_truth": gt[clip][campo],
                   "acierta": acierta[campo], "estado": resumir_estado(estados[campo]), "estados": estados[campo],
                   "error": dato.get("error")} for campo, dato in campos.items()]
    return pd.DataFrame(filas)


def resumir_estado(estado):
    """Un estado por campo: en las listas, el peor de sus elementos (sin_verificar antes que no_mencionado)."""
    etiquetas = _config()["verificacion"]
    if not isinstance(estado, list):
        return estado
    planos = [e["item"] if isinstance(e, dict) else e for e in estado]
    for peor in (etiquetas["etiqueta_no_verificado"], etiquetas["etiqueta_no_mencionado"]):
        if peor in planos:
            return peor
    return etiquetas["etiqueta_verificado"] if planos else etiquetas["etiqueta_no_mencionado"]


def trampas(por_camino: dict) -> pd.DataFrame:
    """Cómo resuelve cada camino las trampas: valor, si acierta y estado.

    Args:
        por_camino: {"reglas": registro(...), "llm": registro(...)} sobre los mismos clips.
    """
    filas = []
    for clip, trampa, campo in TRAMPAS:
        fila = {"clip": clip, "trampa": trampa, "campo": campo}
        for camino, tabla in por_camino.items():
            f = tabla[(tabla["clip"] == clip) & (tabla["campo"] == campo)]
            if f.empty:
                continue
            f = f.iloc[0]
            fila |= {f"{camino}_valor": f["valor"], f"{camino}_acierta": f["acierta"], f"{camino}_estado": f["estado"]}
        filas.append(fila)
    return pd.DataFrame(filas)


def fuera_del_glosario(extraidos: dict, textos: dict) -> pd.DataFrame:
    """Tecnologías extraídas que no están en asr.glosario.tecnologias, con su estado y si están en el ground truth."""
    glosario = {normalizar_texto(t) for t in _config()["asr"]["glosario"]["tecnologias"]}
    gt = _gt()
    filas = []
    for clip, campos in extraidos.items():
        if _esquema(clip) != "entrevista":
            continue
        estados = verificar(campos, textos[clip])["tecnologias"]
        en_gt = {normalizar_texto(t) for t in gt[clip]["tecnologias"]}
        filas += [{"clip": clip, "tecnologia": t, "estado": e, "en_ground_truth": normalizar_texto(t) in en_gt,
                   "evidencia": ev}
                  for t, e, ev in zip(campos["tecnologias"]["valor"] or [], estados, campos["tecnologias"]["evidencia"] or [])
                  if normalizar_texto(t) not in glosario]
    return pd.DataFrame(filas, columns=["clip", "tecnologia", "estado", "en_ground_truth", "evidencia"])


def evidencia_literal(extraidos: dict, textos: dict) -> pd.DataFrame:
    """Cada evidencia no nula: si aparece tal cual en la transcripción y si aparece después de normalizar."""
    filas = []
    for clip, campos in extraidos.items():
        texto = " ".join(textos[clip].split())
        normalizado = f" {normalizar_texto(texto)} "
        for campo, dato in campos.items():
            evidencias = dato.get("menciones") if campo == "items" else dato["evidencia"]
            for ev in evidencias if isinstance(evidencias, list) else [evidencias]:
                if ev:
                    filas.append({"clip": clip, "campo": campo, "evidencia": ev, "literal": ev in texto,
                                  "normalizada": f" {normalizar_texto(ev)} " in normalizado})
    return pd.DataFrame(filas)


def gt_en_texto(clip: str, texto: str) -> dict:
    """{campo: True/False} si el valor del ground truth aparece literal en el texto; None si no aplica
    (items y fechas, que se verifican por su mención y no por el valor, y los campos nulos o en 0)."""
    gt = _gt()[clip]
    tipos = _config()["esquemas"][_esquema(clip)]["campos"]
    salida = {}
    for campo, valor in gt.items():
        if tipos[campo] in ("lista_objetos", "fecha") or valor in (None, 0):
            salida[campo] = None
            continue
        estado = verificar({campo: {"valor": valor, "evidencia": None}}, texto)[campo]
        salida[campo] = resumir_estado(estado) == _config()["verificacion"]["etiqueta_verificado"]
    return salida


def _esquema(clip):
    return {"e": "entrevista", "l": "pedido"}[clip[0]]


@cache
def _gt():
    return {**ground_truth("entrevista"), **ground_truth("pedido")}


@cache
def _config():
    return cargar_config()
