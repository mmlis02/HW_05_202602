"""Validación aritmética del pedido y diagnóstico de la causa cuando no cuadra.

El registro puede venir como valores (campo -> valor) o como lo devuelve extraer()
(campo -> {"valor": ..., "evidencia": ..., "menciones": ...}). Parámetros en config.yaml -> validacion.

validar_total(registro)
    esperado = Σ cantidad × precio_unitario − descuento. Cuadra si |total_dicho − esperado| <=
    tolerancia_total_soles. Si falta un precio, el total o los ítems, el pedido no es validable
    (cuadra = None): la validación no inventa lo que falta.

explicar_diferencia(registro)
    Busca una causa simple que dé exactamente la diferencia (total_dicho − esperado):
    - humana: olvidar el descuento (+descuento) o aplicarlo dos veces (−descuento); omitir una unidad
      (−precio) o un ítem completo (−cantidad × precio); cobrar una unidad de más (+precio) o contar un
      ítem dos veces (+cantidad × precio); cobrar un tamaño por otro de la misma carta (una unidad o
      todas).
    - ambigua: un salto de 1, 10 o 100 (saltos_ambiguos). Puede ser una suma mal llevada o un número
      mal oído ("ciento treinta" por "ciento cuarenta"), así que explica pero no señala a nadie.
    Solo causas de un paso: con combinaciones de dos, casi cualquier diferencia tendría explicación.
    Si nada coincide: "sin explicación".

diagnosticar(registro, palabras)
    Decide si la discrepancia viene del ASR o del hablante con tres señales:
    a) probabilidad: la mínima de las palabras numéricas del total y de los ítems (word.probability de
       faster-whisper). Por debajo de umbral_probabilidad_palabra es señal de ASR. Una probabilidad alta no
       prueba nada: un modelo puede equivocarse con confianza.
    b) repetición: el total dicho aparece dos o más veces ("noventa y cinco soles" ... "Noventa y cinco,
       ok"). Que el ASR se equivoque igual dos veces es poco probable: señal de hablante.
    c) explicación humana: explicar_diferencia encuentra una causa de tipo humana. Señal de hablante.
    Decisión: con señal de ASR y ninguna de hablante -> "asr"; con señales de los dos lados ->
    "indeterminado" (conflicto); solo de hablante -> "hablante"; ninguna -> "indeterminado".
    Sin probabilidades (transcripciones de referencia) no hay señal a): el resultado solo puede ser
    "hablante" o "indeterminado", y la razón lo dice.
"""

from functools import cache

import pandas as pd

from src.config import cargar_config
from src.normalizacion import normalizar_texto, palabras_a_numeros


def validar_total(registro: dict) -> dict:
    """Comprueba que sum(cantidad * precio_unitario) - descuento == total_dicho.

    Returns:
        dict con esperado, dicho, diferencia (dicho - esperado), cuadra (bool, o None si no se puede
        validar) y motivo (por qué no se puede validar, o None).
    """
    items, dicho = _valor(registro, "items"), _valor(registro, "total_dicho")
    descuento = _valor(registro, "descuento") or 0
    motivo = ("no hay ítems" if not items else "no hay total dicho" if dicho is None
              else "falta el precio de algún ítem" if any(i["precio_unitario"] is None for i in items) else None)
    if motivo:
        return {"esperado": None, "dicho": dicho, "diferencia": None, "cuadra": None, "motivo": motivo}
    esperado = sum(i["cantidad"] * i["precio_unitario"] for i in items) - descuento
    diferencia = dicho - esperado
    return {"esperado": esperado, "dicho": dicho, "diferencia": diferencia,
            "cuadra": abs(diferencia) <= _config()["validacion"]["tolerancia_total_soles"], "motivo": None}


def explicar_diferencia(registro: dict) -> dict:
    """Busca una causa concreta y simple para un total que no cuadra.

    Returns:
        dict con explicacion (la primera causa, "cuadra", "no validable" o "sin explicación"),
        tipo ("humana", "ambigua" o None) y candidatas (todas las causas que coinciden).
    """
    v = validar_total(registro)
    if v["cuadra"] is None:
        return {"explicacion": "no validable", "tipo": None, "candidatas": []}
    if v["cuadra"]:
        return {"explicacion": "cuadra", "tipo": None, "candidatas": []}
    cfg = _config()["validacion"]
    diferencia, tolerancia = v["diferencia"], cfg["tolerancia_total_soles"]
    candidatas = []

    def probar(valor, causa, tipo):
        if abs(diferencia - valor) <= tolerancia and causa not in (c["causa"] for c in candidatas):
            candidatas.append({"causa": causa, "tipo": tipo})

    descuento = _valor(registro, "descuento") or 0
    if descuento:
        promocion = _valor(registro, "promocion") or "la promoción"
        probar(descuento, f"se olvidó el descuento de {promocion} ({descuento})", "humana")
        probar(-descuento, f"se aplicó dos veces el descuento de {promocion} ({descuento})", "humana")
    carta = _carta()
    for item in _valor(registro, "items"):
        nombre, cantidad, precio = f"{item['producto']} {item['tamano']}", item["cantidad"], item["precio_unitario"]
        probar(-precio, f"se omitió una unidad de {nombre} ({precio})", "humana")
        probar(precio, f"se cobró una unidad de más de {nombre} ({precio})", "humana")
        if cantidad > 1:
            probar(-cantidad * precio, f"se omitió el ítem completo {cantidad}× {nombre} ({cantidad * precio})", "humana")
            probar(cantidad * precio, f"se contó dos veces el ítem {cantidad}× {nombre} ({cantidad * precio})", "humana")
        otros = carta[(carta.producto == item["producto"]) & ~carta.tamano.str.startswith(str(item["tamano"]))]
        for _, otro in otros.iterrows():
            salto = int(otro.precio) - precio
            probar(salto, f"se cobró una unidad de {nombre} como {otro.tamano} ({salto:+d})", "humana")
            if cantidad > 1:
                probar(salto * cantidad, f"se cobraron las {cantidad} unidades de {nombre} como {otro.tamano} "
                                         f"({salto * cantidad:+d})", "humana")
    for salto in cfg["saltos_ambiguos"]:
        for signo in (1, -1):
            probar(signo * salto, f"salto de {signo * salto:+d}: suma mal llevada o número mal oído", "ambigua")
    candidatas.sort(key=lambda c: c["tipo"] != "humana")
    if not candidatas:
        return {"explicacion": "sin explicación", "tipo": None, "candidatas": []}
    return {"explicacion": candidatas[0]["causa"], "tipo": candidatas[0]["tipo"], "candidatas": candidatas}


def diagnosticar(registro: dict, palabras: list[dict]) -> dict:
    """Decide si la discrepancia del total viene del ASR o del hablante.

    Args:
        registro: pedido extraído.
        palabras: palabras de la transcripción en orden, cada una {"word": str, "probability": float o None},
            como las da faster-whisper con word_timestamps=True.

    Returns:
        dict con diagnostico ("asr", "hablante", "indeterminado", o None si el total cuadra),
        razon (texto) y senales (los valores de las tres señales).
    """
    v = validar_total(registro)
    if v["cuadra"] is None:
        return {"diagnostico": "indeterminado", "razon": f"no se puede validar: {v['motivo']}", "senales": {}}
    if v["cuadra"]:
        return {"diagnostico": None, "razon": "el total cuadra: no hay nada que diagnosticar", "senales": {}}

    cfg = _config()["validacion"]
    textos = [p["word"] for p in palabras]
    hay_probabilidades = bool(palabras) and all(p.get("probability") is not None for p in palabras)
    menciones_total = _ubicar(textos, str(v["dicho"]))
    tramos = menciones_total + [t for m in _menciones_items(registro) for t in _ubicar(textos, m)]
    numericas = sorted({k for inicio, fin in tramos for k in range(inicio, fin) if _es_numerica(textos[k])})
    explicacion = explicar_diferencia(registro)

    minima = min((palabras[k]["probability"] for k in numericas), default=None) if hay_probabilidades else None
    senal_asr = minima is not None and minima < cfg["umbral_probabilidad_palabra"]
    repetido = len(menciones_total) >= 2
    humana = explicacion["tipo"] == "humana"

    razones = []
    if not hay_probabilidades:
        razones.append("sin probabilidades por palabra: solo se usan la repetición y la explicación")
    elif minima is None:
        razones.append("no se ubicaron en la transcripción las palabras numéricas del total ni de los ítems")
    elif senal_asr:
        peor = min(numericas, key=lambda k: palabras[k]["probability"])
        razones.append(f"palabra numérica con probabilidad baja: {textos[peor].strip()!r} = {minima:.2f} "
                       f"< {cfg['umbral_probabilidad_palabra']}")
    else:
        razones.append(f"todas las palabras numéricas con probabilidad >= {cfg['umbral_probabilidad_palabra']} "
                       f"(mínima {minima:.2f}); no descarta al ASR por sí sola")
    veces = len(menciones_total)
    razones.append(f"el total {v['dicho']} se dice {veces} {'vez' if veces == 1 else 'veces'}"
                   + (": es poco probable que el ASR se equivoque igual dos veces" if repetido else ""))
    razones.append(f"explicación: {explicacion['explicacion']}"
                   + (f" ({explicacion['tipo']})" if explicacion["tipo"] else ""))

    if senal_asr and not (repetido or humana):
        diagnostico = "asr"
    elif senal_asr:
        diagnostico, razones = "indeterminado", ["conflicto entre señales"] + razones
    elif repetido or humana:
        diagnostico = "hablante"
    else:
        diagnostico = "indeterminado"
    return {"diagnostico": diagnostico, "razon": "; ".join(razones),
            "senales": {"hay_probabilidades": hay_probabilidades, "probabilidad_minima": minima,
                        "palabras_numericas": [textos[k].strip() for k in numericas],
                        "menciones_total": len(menciones_total), "explicacion": explicacion["explicacion"],
                        "tipo_explicacion": explicacion["tipo"]}}


def _ubicar(textos, frase):
    """Tramos (inicio, fin) de palabras consecutivas que, normalizadas, dan la frase normalizada."""
    objetivo = normalizar_texto(frase)
    maximo = _config()["validacion"]["max_palabras_mencion"]
    tramos, i = [], 0
    while i < len(textos):
        largo = next((n for n in range(min(maximo, len(textos) - i), 0, -1)
                      if _puede_empezar(textos[i]) and normalizar_texto(" ".join(textos[i:i + n])) == objetivo), 0)
        if largo:
            tramos.append((i, i + largo))
        i += largo or 1
    return tramos


def _puede_empezar(palabra):
    """Un número o la mención de un ítem empiezan por una cifra o por un artículo ("un pollo")."""
    limpia = palabra.strip(" ¿?¡!.,;:…").lower()
    return _es_numerica(palabra) or limpia in _config()["normalizacion"]["articulos"]


def _es_numerica(palabra):
    return any(c.isdigit() for c in palabras_a_numeros(palabra.strip(" ¿?¡!.,;:…")))


def _menciones_items(registro):
    dato = registro.get("items")
    return (dato.get("menciones") or []) if isinstance(dato, dict) else []


def _valor(registro, campo):
    dato = registro.get(campo)
    return dato["valor"] if isinstance(dato, dict) and "valor" in dato else dato


@cache
def _carta():
    return pd.read_csv(_config()["rutas"]["carta"])


@cache
def _config():
    return cargar_config()
