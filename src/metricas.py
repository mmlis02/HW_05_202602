"""Métricas de las dos capas: transcripción (WER, CER) y registro (exactitud, macro F1, error absoluto)."""


def wer_cer(referencia: str, hipotesis: str) -> dict:
    """WER y CER entre dos textos ya normalizados."""
    raise NotImplementedError


def exactitud_por_campo(predichos: list[dict], verdaderos: list[dict]) -> dict[str, float]:
    """Proporción de clips en que cada campo coincide con el ground truth."""
    raise NotImplementedError


def macro_f1(verdaderos: list[str], predichos: list[str], clases: list[str]) -> float:
    """Macro F1 para el campo categórico."""
    raise NotImplementedError


def error_absoluto(verdaderos: list[float], predichos: list[float]) -> list[float]:
    """Error absoluto por clip en un campo numérico."""
    raise NotImplementedError


def intervalo_bootstrap(valores: list[float]) -> tuple[float, float]:
    """Intervalo de confianza bootstrap de la media, con nivel e iteraciones de config.yaml."""
    raise NotImplementedError
