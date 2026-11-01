"""Normalización de texto: la misma regla para referencia e hipótesis, y números en palabras a dígitos."""


def normalizar_texto(texto: str) -> str:
    """Aplica la regla de normalización de config.yaml antes de comparar dos textos.

    Minúsculas, sin puntuación, números a dígitos y espacios colapsados.
    """
    raise NotImplementedError


def numeros_a_digitos(texto: str) -> str:
    """Convierte números dichos en palabras a dígitos dentro del texto.

    "seis mil quinientos soles" -> "6500 soles". Es lo que permite verificar 6500 contra
    una transcripción que lo dice en palabras.
    """
    raise NotImplementedError
