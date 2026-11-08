"""Motor único de las dos tareas: audio -> transcripción -> registro verificado.

Es la única puerta que usa app.py. Sirve a los dos esquemas de config.yaml ("entrevista" para
Task 1 y "pedido" para Task 2) sin copiar código. No importa ninguna librería de UI.

Pasos de procesar():
1. transcribir (src.transcripcion) con config.yaml -> asr: modelo, dispositivo, la precisión del device
   resuelto y el glosario (tecnologías + restaurante) con asr.glosario_mecanismo. Si ese mecanismo es
   null, se transcribe sin glosario.
2. normalizar: normalizar_texto, la misma regla que usan el WER y la verificación.
3. extraer con extraer_registro: el método de config.yaml -> extraccion.metodo ("reglas" o "llm") y, si es
   "reglas", los campos de extraccion.campos_llm con el LLM (ver extraer_registro).
4. verificar cada campo contra la transcripción.
5. validar, solo si el esquema es "pedido": validar_total, explicar_diferencia y diagnosticar, este
   último con las palabras y su probabilidad.
Si un paso falla, `error` dice cuál y por qué, se devuelve lo que se alcanzó a calcular y la excepción no
llega a la app.
"""

import time
from functools import cache

from src.config import cargar_config

__all__ = ["procesar", "extraer_registro"]


def procesar(audio_path: str, schema: str) -> dict:
    """Transcribe un audio y extrae el registro del esquema pedido.

    Args:
        audio_path: ruta al archivo de audio.
        schema: nombre de un esquema de config.yaml ("entrevista" o "pedido").

    Returns:
        dict con las claves:
            transcript (str): transcripción completa.
            transcript_normalizado (str): la transcripción tras normalizar_texto.
            campos (dict): valores extraídos según el esquema, cada uno con valor y evidencia.
            campos_verificados (dict): estado de cada campo según src.verificacion:
                "verificado", "verificado_carta" (solo precios), "sin_verificar" o "no_mencionado".
            validacion (dict | None): solo para "pedido": esperado, dicho, diferencia, cuadra,
                explicacion y diagnostico.
            device (str): dispositivo que usó la librería, leído en tiempo de ejecución.
            tiempo_s (float): segundos de procesamiento, de punta a punta.
            error (str | None): mensaje si algo falló; el motor no lanza la excepción a la app.
    """
    inicio = time.perf_counter()
    salida = {"transcript": None, "transcript_normalizado": None, "campos": None, "campos_verificados": None,
              "validacion": None, "device": None, "tiempo_s": None, "error": None}
    paso = "esquema"
    try:
        cfg = _config()
        if schema not in cfg["esquemas"]:
            raise ValueError(f"esquema desconocido: {schema!r}; válidos: {', '.join(cfg['esquemas'])}")

        paso = "transcribir"
        from src.transcripcion import transcribir

        asr = cfg["asr"]
        glosario = [*asr["glosario"]["tecnologias"], *asr["glosario"]["restaurante"]] if asr["glosario_mecanismo"] else None
        transcripcion = transcribir(audio_path, asr["modelo"], asr["dispositivo"], None, glosario)
        salida["transcript"], salida["device"] = transcripcion["texto"], transcripcion["device"]

        paso = "normalizar"
        from src.normalizacion import normalizar_texto

        salida["transcript_normalizado"] = normalizar_texto(transcripcion["texto"])

        paso = "extraer"
        campos = extraer_registro(transcripcion["texto"], schema)
        salida["campos"] = campos

        paso = "verificar"
        from src.verificacion import verificar

        salida["campos_verificados"] = verificar(campos, transcripcion["texto"])

        if schema == "pedido":
            paso = "validar"
            from src.validacion import diagnosticar, explicar_diferencia, validar_total

            salida["validacion"] = {**validar_total(campos), "explicacion": explicar_diferencia(campos),
                                    "diagnostico": diagnosticar(campos, transcripcion["palabras"])}
    except Exception as e:  # el motor nunca lanza a la app: el error viaja en la respuesta
        salida["error"] = f"{paso}: {type(e).__name__}: {e}"
    salida["tiempo_s"] = round(time.perf_counter() - inicio, 3)
    return salida


def extraer_registro(transcript: str, schema: str) -> dict:
    """El registro que usa el motor: extraccion.metodo y, sobre las reglas, los campos de extraccion.campos_llm.

    Con metodo "reglas", los campos de campos_llm que pertenecen al esquema se toman del LLM; si el LLM no
    devuelve ese campo (Ollama caído, JSON inválido), se queda el de las reglas con el error del LLM en
    "error_llm". Cada campo lleva "metodo" con el camino del que salió. La verificación no cambia.
    """
    extraccion = _config()["extraccion"]
    campos = _extractor(extraccion["metodo"])(transcript, schema)
    for dato in campos.values():
        dato["metodo"] = extraccion["metodo"]
    pedidos = [c for c in extraccion.get("campos_llm") or [] if c in campos]
    if extraccion["metodo"] == "reglas" and pedidos:
        del_llm = _extractor("llm")(transcript, schema)
        for campo in pedidos:
            if del_llm[campo].get("error"):
                campos[campo]["error_llm"] = del_llm[campo]["error"]
            else:
                campos[campo] = {**del_llm[campo], "metodo": "llm"}
    return campos


def _extractor(metodo):
    if metodo == "reglas":
        from src.extraccion_reglas import extraer
    elif metodo == "llm":
        from src.extraccion_llm import extraer
    else:
        raise ValueError(f"método de extracción desconocido: {metodo!r}")
    return extraer


@cache
def _config():
    return cargar_config()
