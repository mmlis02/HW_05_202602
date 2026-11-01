"""Regla de verificación: todo valor extraído debe existir literalmente en la transcripción."""


def verificar(campos: dict, transcript: str) -> dict[str, bool]:
    """Marca cada campo como verificado o sin_verificar.

    Un campo se verifica solo si su valor aparece en la transcripción después de normalizar
    ambos lados. Un valor correcto que no se dijo (p. ej. 2.5 años sumados en E4) queda sin_verificar.
    """
    raise NotImplementedError
