"""Extracción por reglas (expresiones regulares) para los esquemas de config.yaml."""


def extraer(transcript: str, schema: str) -> dict:
    """Extrae los campos del esquema con expresiones regulares.

    Returns:
        dict campo -> {"valor": ..., "evidencia": fragmento de la transcripción o None}.
    """
    raise NotImplementedError
