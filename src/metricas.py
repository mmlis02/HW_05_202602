"""Métricas de las dos capas: transcripción (WER, CER) y registro (exactitud, macro F1, error absoluto).

Capa de registro. Un campo acierta según su tipo (config.yaml -> esquemas):
- numerico: la misma cifra.
- numerico_moneda: el mismo monto y la misma moneda.
- texto y texto_o_nulo: iguales tras normalizar_texto (mayúsculas y puntuación no cuentan); dos nulos
  coinciden.
- lista: el mismo conjunto de elementos tras normalizar; el orden no cuenta.
- fecha y categorico: el mismo valor.
- lista_objetos: los mismos ítems (producto, tamaño, cantidad, precio), sin importar el orden.

Intervalos (nivel, iteraciones y semilla en config.yaml -> metricas):
- intervalo_bootstrap: percentiles de un estadístico sobre remuestras de los clips.
- intervalo_wilson: para una proporción de aciertos. Con 5 clips, 5 de 5 da un bootstrap de [1, 1],
  que aparenta una certeza que no existe; Wilson da [0.57, 1], que dice lo que la muestra permite.
"""

import json
import random
from functools import cache
from statistics import NormalDist, mean

import pandas as pd

from src.config import cargar_config
from src.normalizacion import normalizar_texto


def wer_cer(referencia: str, hipotesis: str) -> dict:
    """WER y CER entre dos textos ya normalizados."""
    raise NotImplementedError


def ground_truth(schema: str) -> dict[str, dict]:
    """Registro correcto de cada clip del esquema, leído de los CSV de data/ground_truth."""
    rutas = _config()["rutas"]
    if schema == "entrevista":
        tabla = pd.read_csv(rutas["ground_truth_entrevistas"])
        return {f["clip"]: {
            "anios_experiencia": _numero(f["anios_experiencia"]),
            "ultimo_puesto": f["ultimo_puesto"],
            "tecnologias": json.loads(f["tecnologias"]),
            "pretension_salarial": {"monto": _numero(f["pretension_salarial"]), "moneda": f["moneda"]},
            "disponibilidad": f["disponibilidad"],
            "nivel_ingles": f["nivel_ingles"],
        } for _, f in tabla.iterrows()}
    if schema == "pedido":
        tabla = pd.read_csv(rutas["ground_truth_llamadas"])
        return {f["clip"]: {
            "items": json.loads(f["items"]),
            "promocion": None if pd.isna(f["promocion"]) else f["promocion"],
            "descuento": int(f["descuento"]),
            "direccion_entrega": f["direccion_entrega"],
            "metodo_pago": f["metodo_pago"],
            "total_dicho": int(f["total_dicho"]),
        } for _, f in tabla.iterrows()}
    raise ValueError(f"esquema desconocido: {schema!r}")


def aciertos(predicho: dict, verdadero: dict, schema: str) -> dict[str, bool]:
    """Si cada campo del registro predicho coincide con el ground truth."""
    tipos = _config()["esquemas"][schema]["campos"]
    return {campo: _coincide(tipo, predicho.get(campo), verdadero.get(campo)) for campo, tipo in tipos.items()}


def exactitud_por_campo(predichos: list[dict], verdaderos: list[dict], schema: str) -> dict[str, float]:
    """Proporción de clips en que cada campo coincide con el ground truth."""
    filas = [aciertos(p, v, schema) for p, v in zip(predichos, verdaderos, strict=True)]
    return {campo: mean(f[campo] for f in filas) for campo in filas[0]}


def macro_f1(verdaderos: list[str], predichos: list[str], clases: list[str]) -> float:
    """Macro F1 para el campo categórico.

    Promedia el F1 de cada clase. Una clase que no está en el ground truth ni en las predicciones se
    omite, porque su F1 no está definido. Una predicción vacía cuenta como fallo de la clase verdadera.
    """
    f1 = []
    for clase in clases:
        tp = sum(v == clase and p == clase for v, p in zip(verdaderos, predichos, strict=True))
        fp = sum(v != clase and p == clase for v, p in zip(verdaderos, predichos, strict=True))
        fn = sum(v == clase and p != clase for v, p in zip(verdaderos, predichos, strict=True))
        if tp + fp + fn:
            f1.append(2 * tp / (2 * tp + fp + fn))
    return mean(f1) if f1 else float("nan")


def error_absoluto(verdaderos: list[float], predichos: list[float | None]) -> list[float | None]:
    """Error absoluto por clip en un campo numérico; None si no hubo predicción."""
    return [None if p is None else abs(float(p) - float(v)) for v, p in zip(verdaderos, predichos, strict=True)]


def intervalo_bootstrap(valores: list, estadistico=mean) -> tuple[float, float]:
    """Intervalo de confianza bootstrap de un estadístico (la media, por defecto) sobre los clips."""
    cfg = _config()["metricas"]
    if not valores:
        return float("nan"), float("nan")
    rng = random.Random(cfg["semilla"])
    remuestras = sorted(estadistico(rng.choices(valores, k=len(valores))) for _ in range(cfg["bootstrap_iteraciones"]))
    cola = (1 - cfg["intervalo_confianza"]) / 2
    return remuestras[int(cola * len(remuestras))], remuestras[int((1 - cola) * len(remuestras)) - 1]


def intervalo_wilson(exitos: int, n: int) -> tuple[float, float]:
    """Intervalo de Wilson para una proporción de aciertos."""
    if n == 0:
        return float("nan"), float("nan")
    z = NormalDist().inv_cdf(1 - (1 - _config()["metricas"]["intervalo_confianza"]) / 2)
    p = exitos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margen = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return max(0.0, centro - margen), min(1.0, centro + margen)


def _coincide(tipo, p, v):
    if tipo == "texto_o_nulo" and p is None and v is None:
        return True
    if p is None or v is None:
        return False
    if tipo == "numerico":
        return abs(float(p) - float(v)) < 1e-9
    if tipo == "numerico_moneda":
        return abs(float(p["monto"]) - float(v["monto"])) < 1e-9 and p["moneda"] == v["moneda"]
    if tipo in ("texto", "texto_o_nulo"):
        return normalizar_texto(str(p)) == normalizar_texto(str(v))
    if tipo == "lista":
        return {normalizar_texto(x) for x in p} == {normalizar_texto(x) for x in v}
    if tipo in ("fecha", "categorico"):
        return p == v
    if tipo == "lista_objetos":
        def clave(i):
            return (i["producto"], normalizar_texto(str(i["tamano"])), i["cantidad"], i["precio_unitario"])
        return sorted(map(clave, p)) == sorted(map(clave, v))
    raise ValueError(f"tipo desconocido: {tipo!r}")


def _numero(valor):
    return int(valor) if float(valor).is_integer() else float(valor)


@cache
def _config():
    return cargar_config()
