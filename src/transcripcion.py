"""Transcripción con faster-whisper y lectura del device real en tiempo de ejecución."""


def transcribir(
    audio_path: str,
    modelo: str,
    device: str,
    compute_type: str,
    glosario: list[str] | None = None,
) -> dict:
    """Transcribe un audio con un modelo, device y precisión dados.

    Separada del motor para que 02_transcripcion_gpu pueda variar modelo, device y precisión
    sin pasar por la extracción.

    Returns:
        dict con texto, palabras (con probabilidad), device leído de la librería,
        compute_type efectivo, duracion_audio_s, tiempo_s y vram_pico_mb.
    """
    raise NotImplementedError
