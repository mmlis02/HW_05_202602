"""Validación aritmética del pedido y diagnóstico de la causa cuando no cuadra."""


def validar_total(pedido: dict) -> dict:
    """Comprueba que sum(cantidad * precio_unitario) - descuento == total_dicho.

    Returns:
        dict con total_calculado, total_dicho, diferencia y cuadra (bool).
    """
    raise NotImplementedError


def diagnosticar(pedido: dict, palabras: list[dict]) -> str:
    """Decide si una discrepancia viene del ASR o del hablante.

    Args:
        pedido: registro extraído.
        palabras: palabras de la transcripción con su probabilidad.

    Returns:
        "asr" o "hablante".
    """
    raise NotImplementedError
