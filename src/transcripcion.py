"""Transcripción con faster-whisper, con el device y la VRAM medidos en tiempo de ejecución.

- Device y precisión: se leen del modelo cargado (CTranslate2: model.model.device y .compute_type), no
  de config.yaml. Con "auto", una GPU ausente cae a CPU sin avisar; solo esta lectura lo delata.
- VRAM: faster-whisper corre sobre CTranslate2, no sobre PyTorch, así que torch.cuda.max_memory_allocated
  no ve su memoria. Un hilo aparte consulta con pynvml la memoria usada de la GPU cada vram_intervalo_s
  mientras se transcribe y guarda el máximo (vram_pico_mb). vram_base_mb es la memoria usada antes de
  cargar el modelo: pico - base es lo que ocupa esta corrida. Sin GPU NVIDIA, las dos quedan en None.
- Palabras: con word_timestamps, cada palabra trae su probabilidad. El diagnóstico de src/validacion.py
  la necesita.
- Glosario: faster-whisper 1.2.1 acepta initial_prompt (contexto de la primera ventana, que se diluye
  después) y hotwords (se antepone en cada ventana). Se elige con `mecanismo`: "initial_prompt",
  "hotwords" o "ambos".
- Caché: cada transcripción se guarda como JSON en <raiz>/<cache.patron_transcripcion>. Guarda solo el
  nombre del archivo de audio, nunca su ruta en Drive.
- CUDA 12 en un sistema con otra versión (Colab con CUDA 13): CTranslate2 abre libcublas.so.12 y
  libcudnn*.so.9 por nombre con dlopen. Si el sistema no las trae, se instalan con pip
  (requirements-gpu.txt) y precargar_cuda12() las carga en el proceso con ctypes y RTLD_GLOBAL, antes del
  primer uso de la GPU. Después, el dlopen de CTranslate2 encuentra la librería ya cargada por su soname.
  Cambiar LD_LIBRARY_PATH con el proceso ya iniciado no sirve: el cargador la lee al arrancar.
"""

import ctypes
import gc
import json
import sys
import threading
import time
from datetime import datetime, timezone
from functools import cache
from pathlib import Path

from src.config import cargar_config

_MODELOS = {}

# Orden de carga: cada librería después de las que necesita (libcublasLt antes que libcublas; las
# subbibliotecas de cuDNN 9 antes que libcudnn). Son los nombres de los wheels de requirements-gpu.txt.
_CUDA12 = {
    "cublas": ["libcublasLt.so.12", "libcublas.so.12"],
    "cudnn": ["libcudnn_graph.so.9", "libcudnn_engines_precompiled.so.9", "libcudnn_engines_runtime_compiled.so.9",
              "libcudnn_heuristic.so.9", "libcudnn_ops.so.9", "libcudnn_cnn.so.9", "libcudnn_adv.so.9",
              "libcudnn.so.9"],
}


def transcribir(
    audio: str | Path,
    modelo: str,
    device: str = "auto",
    compute_type: str | None = None,
    glosario: list[str] | None = None,
    mecanismo: str | None = None,
) -> dict:
    """Transcribe un audio con un modelo, device y precisión dados.

    Args:
        audio: ruta del archivo.
        modelo: nombre de faster-whisper ("small", "large-v3").
        device: "cuda", "cpu" o "auto".
        compute_type: "float16", "int8"...; None usa la de config.yaml para el device resuelto.
        glosario: términos del dominio; None o vacío transcribe sin glosario.
        mecanismo: cómo se pasa el glosario; None usa asr.glosario_mecanismo.

    Returns:
        dict con texto, palabras (word, start, end, probability), segmentos, idioma,
        duracion_audio_s, modelo, device y compute_type leídos del modelo, glosario (mecanismo usado o
        None), tiempo_s, segundos_por_minuto, tiempo_carga_s, vram_base_mb, vram_pico_mb y versiones.
    """
    cfg = _config()
    asr = cfg["asr"]
    whisper, carga = cargar_modelo(modelo, device, compute_type)
    opciones = {"language": cfg["proyecto"]["idioma"], "beam_size": asr["beam_size"],
                "vad_filter": asr["vad_filter"], "word_timestamps": asr["word_timestamps"]}
    mecanismo = (mecanismo or asr["glosario_mecanismo"]) if glosario else None
    if mecanismo:
        if mecanismo not in ("initial_prompt", "hotwords", "ambos"):
            raise ValueError(f"mecanismo de glosario desconocido: {mecanismo!r}")
        texto_glosario = ", ".join(glosario)
        if mecanismo in ("initial_prompt", "ambos"):
            opciones["initial_prompt"] = texto_glosario
        if mecanismo in ("hotwords", "ambos"):
            opciones["hotwords"] = texto_glosario

    with _MonitorVRAM(asr["vram_intervalo_s"]) as monitor:
        inicio = time.perf_counter()
        segmentos, info = whisper.transcribe(str(audio), **opciones)
        segmentos = list(segmentos)  # el generador es perezoso: la transcripción ocurre aquí
        tiempo = time.perf_counter() - inicio

    import ctranslate2
    import faster_whisper

    return {
        "texto": " ".join(s.text.strip() for s in segmentos).strip(),
        "palabras": [{"word": w.word, "start": round(float(w.start), 3), "end": round(float(w.end), 3),
                      "probability": round(float(w.probability), 4)} for s in segmentos for w in (s.words or [])],
        "segmentos": [{"start": round(float(s.start), 3), "end": round(float(s.end), 3), "text": s.text.strip()}
                      for s in segmentos],
        "idioma": info.language,
        "duracion_audio_s": round(info.duration, 3),
        "modelo": modelo,
        "device": carga["device"],
        "compute_type": carga["compute_type"],
        "glosario": mecanismo,
        "tiempo_s": round(tiempo, 3),
        "segundos_por_minuto": round(tiempo / (info.duration / 60), 3) if info.duration else None,
        "tiempo_carga_s": carga["tiempo_carga_s"],
        "vram_base_mb": carga["vram_base_mb"],
        "vram_pico_mb": monitor.pico,
        "versiones": {"faster_whisper": faster_whisper.__version__, "ctranslate2": ctranslate2.__version__},
    }


def cargar_modelo(modelo: str, device: str = "auto", compute_type: str | None = None):
    """Carga (o reutiliza) un modelo y devuelve (WhisperModel, datos de la carga).

    Los datos de la carga traen el device y la precisión que reporta CTranslate2, el tiempo de carga y
    la VRAM usada antes de cargar.
    """
    resuelto = _resolver_device(device)
    compute_type = compute_type or _config()["asr"]["compute_type"][resuelto]
    clave = (modelo, device, compute_type)
    if clave not in _MODELOS:
        if resuelto == "cuda":
            precargar_cuda12()
        from faster_whisper import WhisperModel

        base = vram_usada_mb()
        inicio = time.perf_counter()
        whisper = WhisperModel(modelo, device=device, compute_type=compute_type,
                               download_root=str(_config()["rutas"]["modelos_dir"]))
        _MODELOS[clave] = (whisper, {
            "device": whisper.model.device, "compute_type": whisper.model.compute_type,
            "tiempo_carga_s": round(time.perf_counter() - inicio, 3), "vram_base_mb": base,
        })
    return _MODELOS[clave]


@cache
def precargar_cuda12() -> list[str]:
    """Carga en este proceso cuBLAS 12 y cuDNN 9 instalados con pip, si están instalados.

    Busca nvidia/cublas/lib y nvidia/cudnn/lib en sys.path: estos wheels no traen __init__.py, así que
    `nvidia.cublas.lib.__file__` no sirve para ubicarlos. Si un orden no alcanza, reintenta las que fallaron
    mientras alguna nueva cargue.

    Returns:
        Las librerías cargadas; vacío si los paquetes no están (CPU, macOS o CUDA 12 del sistema).

    Raises:
        OSError: si los paquetes están pero alguna librería no carga.
    """
    pendientes = []
    for paquete, librerias in _CUDA12.items():
        carpeta = next((Path(p) / "nvidia" / paquete / "lib" for p in sys.path
                        if (Path(p) / "nvidia" / paquete / "lib").is_dir()), None)
        if carpeta:
            pendientes += [carpeta / nombre for nombre in librerias if (carpeta / nombre).exists()]
    cargadas, errores = [], {}
    while pendientes:
        fallidas = []
        for ruta in pendientes:
            try:
                ctypes.CDLL(str(ruta), mode=ctypes.RTLD_GLOBAL)
                cargadas.append(ruta.name)
            except OSError as e:
                fallidas.append(ruta)
                errores[ruta.name] = str(e)
        if len(fallidas) == len(pendientes):
            raise OSError("no se pudieron cargar: " + "; ".join(f"{r.name}: {errores[r.name]}" for r in fallidas))
        pendientes = fallidas
    return cargadas


def liberar_modelos() -> None:
    """Descarga los modelos cargados, para que la VRAM de una corrida no se sume a la siguiente."""
    _MODELOS.clear()
    gc.collect()


def vram_usada_mb() -> float | None:
    """Memoria usada en la GPU 0 según pynvml, en MB; None si no hay GPU NVIDIA."""
    handle = _handle_nvml()
    if handle is None:
        return None
    import pynvml

    return round(pynvml.nvmlDeviceGetMemoryInfo(handle).used / 2**20, 1)


def id_corrida(modelo: str, compute_type: str, device: str, glosario: str | None) -> str:
    """Nombre de la carpeta de caché de una corrida: "large-v3_float16_cuda_sin-glosario"."""
    return f"{modelo}_{compute_type}_{device}_{glosario or 'sin-glosario'}"


def ruta_cache(raiz: str | Path, corrida: str, clip: str) -> Path:
    return Path(raiz) / _config()["cache"]["patron_transcripcion"].format(corrida=corrida, clip=clip)


def guardar_transcripcion(resultado: dict, raiz: str | Path) -> Path:
    """Guarda una transcripción (con sus claves clip y corrida) como JSON en la caché."""
    ruta = ruta_cache(raiz, resultado["corrida"], resultado["clip"])
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    return ruta


def cargar_transcripcion(raiz: str | Path, corrida: str, clip: str) -> dict | None:
    ruta = ruta_cache(raiz, corrida, clip)
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def transcribir_corpus(
    audios: dict[str, Path],
    modelo: str,
    device: str,
    compute_type: str,
    destino: str | Path,
    glosario: list[str] | None = None,
    mecanismo: str | None = None,
    reusar: bool = True,
) -> dict[str, dict]:
    """Transcribe cada clip y lo guarda en la caché de `destino`.

    Con reusar=True, un clip que ya está en la caché se lee en vez de transcribirse otra vez. Así, si la
    sesión de Colab se corta, volver a ejecutar continúa donde quedó.

    Returns:
        dict clip -> resultado de transcribir(), con clip, archivo, corrida y fecha.
    """
    mecanismo = (mecanismo or _config()["asr"]["glosario_mecanismo"]) if glosario else None
    corrida = id_corrida(modelo, compute_type, device, mecanismo)
    resultados = {}
    for clip, audio in audios.items():
        guardado = cargar_transcripcion(destino, corrida, clip) if reusar else None
        if guardado is None:
            r = transcribir(audio, modelo, device, compute_type, glosario, mecanismo)
            guardado = {"clip": clip, "archivo": Path(audio).name, "corrida": corrida,
                        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"), **r}
            guardar_transcripcion(guardado, destino)
            estado = f"{r['tiempo_s']:.1f} s, device {r['device']}"
        else:
            estado = "desde la caché"
        print(f"  {corrida} · {clip}: {estado}", flush=True)
        resultados[clip] = guardado
    return resultados


class _MonitorVRAM:
    """Consulta la memoria usada de la GPU en un hilo aparte y guarda el pico."""

    def __init__(self, intervalo_s):
        self.intervalo_s, self.pico = intervalo_s, None
        self._parar = threading.Event()
        self._hilo = None

    def __enter__(self):
        self.pico = vram_usada_mb()
        if self.pico is not None:
            self._hilo = threading.Thread(target=self._medir, daemon=True)
            self._hilo.start()
        return self

    def _medir(self):
        while not self._parar.wait(self.intervalo_s):
            self.pico = max(self.pico, vram_usada_mb())

    def __exit__(self, *_):
        self._parar.set()
        if self._hilo:
            self._hilo.join()
            self.pico = max(self.pico, vram_usada_mb())


def _resolver_device(device):
    if device != "auto":
        return device
    import ctranslate2

    return "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"


@cache
def _handle_nvml():
    try:
        import pynvml

        pynvml.nvmlInit()
        return pynvml.nvmlDeviceGetHandleByIndex(0)
    except Exception:  # sin pynvml, sin driver NVIDIA o sin GPU: no hay medición
        return None


@cache
def _config():
    return cargar_config()
