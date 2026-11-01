"""Escalera de degradación reproducible: L0 tal cual, L1 WhatsApp, L2 teléfono, L3 ruido."""


def degradar(audio_path: str, nivel: str, salida_path: str) -> str:
    """Genera la versión degradada de un audio según el nivel definido en config.yaml.

    Returns:
        Ruta del archivo generado.
    """
    raise NotImplementedError


def medir_snr(senal_path: str, ruido_path: str) -> float:
    """Relación señal/ruido en dB medida sobre las muestras, no la nominal de config.yaml."""
    raise NotImplementedError
