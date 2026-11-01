"""Regla de verificación: todo valor extraído debe existir literalmente en la transcripción.

Transcripción y valor se normalizan con src.normalizacion.normalizar_texto y el valor se busca como
secuencia de palabras completas ("8" no aparece dentro de "1800"). Cuatro estados (config.yaml ->
verificacion):

- verificado: el valor aparece en la transcripción. Para un campo nulo (o un descuento 0, ver
  cero_es_ausencia), la ausencia se dijo en voz alta: su evidencia es una respuesta que empieza con
  una negación ("No, ninguno.") y aparece literalmente.
- verificado_carta: solo para precio_unitario, que sale de la carta y no del audio. Se reporta aparte
  y nunca se suma a verificado.
- sin_verificar: el valor no aparece, aunque sea correcto (los 2.5 años de E4, que se obtienen
  sumando y nunca se dicen); o un campo nulo cuya evidencia no aparece o no es una negación.
- no_mencionado: campo nulo sin evidencia; el extractor no encontró ninguna mención. No es un fallo de
  verificación y se cuenta aparte para no inflar sin_verificar.

Qué se busca según el tipo del campo (config.yaml -> esquemas):
- numerico: la cifra ("4.5", "96").
- numerico_moneda: el monto y alguna forma de decir la moneda ("soles", "dólares").
- texto: cada parte separada por coma; en una dirección, "Calle Los Cedros 245", "departamento 302"
  y "Surco" por separado, porque al hablar se intercalan palabras ("en Surco").
- categorico y texto_o_nulo: alguna forma de decir la clase ("básico" para basico, "LEÑA5" para promo app).
- lista: cada elemento por separado.
- fecha: la expresión de la evidencia ("en 2 semanas") debe aparecer y, interpretada desde la fecha de
  grabación, dar la fecha extraída. Es una conversión de lo dicho, como "seis mil quinientos" -> 6500.
  En cambio, una suma de dos cosas dichas (E4) no es una conversión y queda sin_verificar.
- lista_objetos (items): cada ítem por separado. Su mención ("2 jarras de chicha morada") debe aparecer,
  y al interpretarla de nuevo debe dar el mismo producto, tamaño y cantidad. El precio es
  verificado_carta si coincide con la carta.
"""

import re
from functools import cache

from src.config import cargar_config
from src.extraccion_reglas import interpretar_fecha, interpretar_item, precio_carta
from src.normalizacion import normalizar_texto, palabras_a_numeros


def verificar(campos: dict, transcript: str) -> dict:
    """Estado de verificación de cada campo extraído.

    Args:
        campos: dict campo -> {"valor": ..., "evidencia": ...}, como lo devuelve extraer().
        transcript: transcripción completa.

    Returns:
        dict campo -> estado. Para tecnologias, una lista de estados; para items, una lista de
        {"item": estado, "precio_unitario": estado}.
    """
    texto = normalizar_texto(transcript)
    return {campo: _verificar_campo(campo, dato, texto) for campo, dato in campos.items()}


def _verificar_campo(campo, dato, texto):
    cfg = _config()
    valor, tipo = dato["valor"], _tipos()[campo]
    if tipo == "lista":
        return [_estado(_aparece(v, texto)) for v in valor or []]
    if tipo == "lista_objetos":
        return [_verificar_item(item, dato.get("menciones") or [], texto) for item in valor or []]
    if valor is None or (valor == 0 and campo in cfg["verificacion"]["cero_es_ausencia"]):
        return _verificar_ausencia(dato["evidencia"], texto)
    if tipo == "numerico":
        return _estado(_aparece(_cifra(valor), texto))
    if tipo == "numerico_moneda":
        monedas = cfg["esquemas"]["entrevista"]["alias"]["moneda"]
        return _estado(_aparece(_cifra(valor["monto"]), texto)
                       and any(_aparece(a, texto) for a in monedas.get(valor["moneda"], [])))
    if tipo in ("categorico", "texto_o_nulo"):
        return _estado(any(_aparece(a, texto) for a in _alias(campo).get(valor, [valor])))
    if tipo == "texto":
        return _estado(all(_aparece(parte, texto) for parte in str(valor).split(", ")))
    if tipo == "fecha":
        encontrada = interpretar_fecha(palabras_a_numeros(dato["evidencia"] or ""))
        return _estado(bool(encontrada) and encontrada[1].isoformat() == valor
                       and _aparece(encontrada[0], texto))
    raise ValueError(f"tipo desconocido: {tipo!r}")


def _verificar_ausencia(evidencia, texto):
    if not evidencia:
        return _config()["verificacion"]["etiqueta_no_mencionado"]
    negacion = _config()["extraccion"]["reglas"]["negacion"]
    patron = r"^(?:" + "|".join(re.escape(normalizar_texto(n)) for n in negacion) + r")(?!\S)"
    return _estado(_aparece(evidencia, texto) and re.match(patron, normalizar_texto(evidencia)) is not None)


def _verificar_item(item, menciones, texto):
    clave = ("producto", "tamano", "cantidad")
    dicho = any(_aparece(m, texto) and (leido := interpretar_item(m))
                and all(leido[k] == item[k] for k in clave) for m in menciones)
    en_carta = item["precio_unitario"] is not None and \
        item["precio_unitario"] == precio_carta(item["producto"], item["tamano"])
    etiquetas = _config()["verificacion"]
    return {"item": _estado(dicho),
            "precio_unitario": etiquetas["etiqueta_carta"] if en_carta else etiquetas["etiqueta_no_verificado"]}


def _aparece(frase, texto):
    buscada = normalizar_texto(str(frase))
    return bool(buscada) and re.search(rf"(?<!\S){re.escape(buscada)}(?!\S)", texto) is not None


def _cifra(valor):
    return f"{float(valor):g}"


def _estado(ok):
    etiquetas = _config()["verificacion"]
    return etiquetas["etiqueta_verificado"] if ok else etiquetas["etiqueta_no_verificado"]


def _alias(campo):
    return next((e["alias"][campo] for e in _config()["esquemas"].values() if campo in e.get("alias", {})), {})


@cache
def _config():
    return cargar_config()


@cache
def _tipos():
    return {campo: tipo for e in _config()["esquemas"].values() for campo, tipo in e["campos"].items()}
