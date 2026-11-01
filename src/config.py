"""Carga de config.yaml, el único lugar con rutas, modelos, umbrales y prompts."""

from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def cargar_config(ruta: str | Path | None = None) -> dict:
    """Lee config.yaml y convierte cada entrada de `rutas` en un Path absoluto.

    Las rutas se resuelven contra la raíz del repositorio, así que el resultado es el mismo
    se llame desde app.py, desde notebooks/ o desde Colab.
    """
    ruta = Path(ruta) if ruta else RAIZ / "config.yaml"
    with open(ruta, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["rutas"] = {nombre: RAIZ / valor for nombre, valor in cfg["rutas"].items()}
    return cfg
