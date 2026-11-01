"""Motor único de las dos tareas: audio -> transcripción -> registro verificado.

Es la única puerta que usa app.py. Sirve a los dos esquemas de config.yaml ("entrevista" para
Task 1 y "pedido" para Task 2) sin copiar código. No importa ninguna librería de UI.
"""

__all__ = ["procesar"]


def procesar(audio_path: str, schema: str) -> dict:
    """Transcribe un audio y extrae el registro del esquema pedido.

    Args:
        audio_path: ruta al archivo de audio.
        schema: nombre de un esquema de config.yaml ("entrevista" o "pedido").

    Returns:
        dict con las claves:
            transcript (str): transcripción completa.
            campos (dict): valores extraídos según el esquema.
            campos_verificados (dict): estado de cada campo según src.verificacion:
                "verificado", "verificado_carta" (solo precios) o "sin_verificar".
            device (str): dispositivo que usó la librería, leído en tiempo de ejecución.
            tiempo_s (float): segundos de procesamiento.
            error (str | None): mensaje si algo falló; el motor no lanza la excepción a la app.
    """
    raise NotImplementedError
