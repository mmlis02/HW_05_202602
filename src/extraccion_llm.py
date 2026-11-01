"""Extracción con un modelo de lenguaje que devuelve JSON estructurado."""


def extraer(transcript: str, schema: str) -> dict:
    """Extrae los campos del esquema con el modelo y el prompt de config.yaml.

    La API key se lee de .env; nunca del código.

    Returns:
        dict campo -> {"valor": ..., "evidencia": fragmento de la transcripción o None}.
    """
    raise NotImplementedError
