"""Ubicación de los audios del corpus por su nombre de archivo.

Los audios son privados: no están en el repositorio, ni el enlace a su carpeta. Se identifican por su
nombre original, sin renombrarlos, con el mapeo de config.yaml -> audios.archivos ("task 1-1" -> e1).
A partir de aquí todo el código usa los clips e1 ... l5.

Cómo se comparan los nombres: sin la extensión (que debe estar en audios.extensiones), sin distinguir
mayúsculas, con los espacios colapsados y en Unicode NFC (Drive y macOS pueden guardar una misma tilde
de dos formas distintas).
"""

import os
import re
import unicodedata
from functools import cache
from pathlib import Path

from src.config import cargar_config


class AudiosIncompletos(Exception):
    """No están los 10 audios, o alguno aparece más de una vez."""


def clip_de_archivo(nombre: str) -> str | None:
    """Clip (e1 ... l5) de un nombre de archivo ("task 1-1.m4a" -> "e1"), o None si no es del corpus."""
    ruta = Path(nombre)
    if ruta.suffix.lower() not in _extensiones():
        return None
    return _mapeo().get(_clave(ruta.stem))


def buscar_audios(raiz: str | Path) -> dict[str, Path]:
    """Busca, bajo `raiz` y en todas sus subcarpetas, un archivo por clip.

    Se salta las carpetas ocultas (como la papelera de Drive).

    Returns:
        dict clip -> ruta del audio, en el orden de config.yaml.

    Raises:
        AudiosIncompletos: si falta algún audio o alguno aparece más de una vez. El mensaje dice cuáles,
            por su nombre original.
    """
    raiz = Path(raiz)
    if not raiz.is_dir():
        raise AudiosIncompletos(f"no existe la carpeta {raiz}")
    encontrados = {}
    for carpeta, subcarpetas, archivos in os.walk(raiz):
        subcarpetas[:] = [s for s in subcarpetas if not s.startswith(".")]
        for archivo in archivos:
            if clip := clip_de_archivo(archivo):
                encontrados.setdefault(clip, []).append(Path(carpeta) / archivo)

    nombres = {clip: nombre for nombre, clip in _config()["audios"]["archivos"].items()}
    faltan = [nombre for clip, nombre in nombres.items() if clip not in encontrados]
    repetidos = {nombres[clip]: rutas for clip, rutas in encontrados.items() if len(rutas) > 1}
    if faltan or repetidos:
        partes = [f"se encontraron {len(encontrados)} de {len(nombres)} audios bajo {raiz}"]
        if faltan:
            partes.append("faltan: " + ", ".join(faltan))
        for nombre, rutas in repetidos.items():
            partes.append(f"repetido {nombre!r}: " + " | ".join(str(r) for r in sorted(rutas)))
        raise AudiosIncompletos("; ".join(partes))
    return {clip: encontrados[clip][0] for clip in nombres}


def duracion_audio_s(ruta: str | Path) -> float:
    """Duración real del audio en segundos, decodificándolo como lo hace faster-whisper (16 kHz, mono)."""
    from faster_whisper import decode_audio

    frecuencia = 16000
    return round(len(decode_audio(str(ruta), sampling_rate=frecuencia)) / frecuencia, 2)


def _clave(nombre):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", nombre)).strip().lower()


@cache
def _mapeo():
    return {_clave(nombre): clip for nombre, clip in _config()["audios"]["archivos"].items()}


@cache
def _extensiones():
    return {e.lower() for e in _config()["audios"]["extensiones"]}


@cache
def _config():
    return cargar_config()
