"""Extracción con un LLM local (Ollama) que devuelve JSON con un esquema fijo.

Mismo contrato que src.extraccion_reglas.extraer: dict campo -> {"valor": ..., "evidencia": ...}. La
verificación es la de siempre (src.verificacion): el LLM no se verifica a sí mismo.

Cómo se llama al modelo (config.yaml -> extraccion.llm y extraccion.prompts):
- Salida estructurada de Ollama: `format` recibe el esquema JSON de esquema_json(schema), así que el modelo
  solo puede generar ese objeto. Las clases (nivel de inglés, moneda, método de pago, promoción, producto y
  tamaño) van como enum, y las listas tienen un tope (max_tecnologias, max_items): en el piloto, sin tope, un
  modelo repitió tecnologías inventadas hasta agotar num_predict. Temperatura 0 y semilla fija.
- Cada campo trae su evidencia: el fragmento literal de la transcripción. En tecnologias e items, una por
  elemento; la de cada ítem es su mención ("2 jarras de chicha morada"), que la verificación vuelve a
  interpretar con las reglas, igual que las menciones de src.extraccion_reglas.
- precio_unitario no lo da el LLM: sale de la carta (extraccion_reglas.precio_carta), como en las reglas,
  para comparar los dos caminos en igualdad de condiciones.
- Si Ollama falla o la respuesta no es un JSON válido, todos los campos quedan nulos con "error"; si un
  solo campo trae un valor inválido (una fecha que no existe), queda nulo ese campo. Nunca se lanza la
  excepción.

Caché (config.yaml -> cache.patron_llm). Cada respuesta se guarda en data/cache/llm/<modelo>/<clave>.json,
con el tiempo y la memoria medidos. La clave es un hash de todo lo que define la respuesta: modelo,
prompts, esquema JSON, opciones y transcripción. Si algo cambia, la clave cambia y se vuelve a llamar; si
no, se lee el archivo y no hace falta Ollama.
"""

import hashlib
import json
import time
from datetime import date, datetime
from functools import cache
from pathlib import Path

from src.config import cargar_config
from src.extraccion_reglas import precio_carta


def extraer(transcript: str, schema: str, modelo: str | None = None) -> dict:
    """Extrae los campos del esquema con el LLM de config.yaml (o `modelo`, para comparar candidatos).

    Returns:
        dict campo -> {"valor": ..., "evidencia": fragmento literal o None}. Un campo que no se pudo
        extraer trae además "error". En items, "menciones" son las evidencias de cada ítem.
    """
    campos = list(_config()["esquemas"][schema]["campos"])
    try:
        datos = json.loads(llamar(transcript, schema, modelo)["respuesta"])
    except Exception as e:  # Ollama caído, tiempo agotado o JSON inválido: el campo queda nulo con el error
        return {campo: {"valor": None, "evidencia": None, "error": f"{type(e).__name__}: {e}"} for campo in campos}
    salida = {}
    for campo in campos:
        try:
            salida[campo] = _convertir(campo, datos[campo])
        except Exception as e:
            salida[campo] = {"valor": None, "evidencia": None, "error": f"{type(e).__name__}: {e}"}
    return salida


def llamar(transcript: str, schema: str, modelo: str | None = None) -> dict:
    """La respuesta del modelo con sus mediciones, de la caché o llamando a Ollama (y guardándola).

    Returns:
        dict con modelo, esquema, clave, respuesta (el JSON en texto), tiempo_s (de punta a punta),
        carga_s, tokens_entrada, tokens_salida, memoria_mb (lo que Ollama reporta para el modelo cargado),
        version_ollama, digest y fecha.
    """
    llm = _config()["extraccion"]["llm"]
    modelo = modelo or llm["modelo"]
    mensajes = _mensajes(transcript, schema)
    formato = esquema_json(schema)
    opciones = {"temperature": llm["temperatura"], "seed": llm["semilla"], "num_ctx": llm["num_ctx"],
                "num_predict": llm["num_predict"]}
    clave = hashlib.sha256(json.dumps([modelo, mensajes, formato, opciones], ensure_ascii=False,
                                      sort_keys=True).encode()).hexdigest()[:20]
    ruta = _ruta_cache(modelo, clave)
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))

    import ollama

    cliente = ollama.Client(host=llm["url"], timeout=llm["timeout_s"])
    inicio = time.perf_counter()
    r = cliente.chat(model=modelo, messages=mensajes, format=formato, options=opciones,
                     keep_alive=llm["keep_alive"])
    tiempo = time.perf_counter() - inicio
    cargado = next((m for m in cliente.ps().models if m.model == modelo), None)
    registro = {
        "modelo": modelo, "esquema": schema, "clave": clave, "respuesta": r.message.content,
        "tiempo_s": round(tiempo, 2), "carga_s": round((r.load_duration or 0) / 1e9, 2),
        "tokens_entrada": r.prompt_eval_count, "tokens_salida": r.eval_count,
        "memoria_mb": round(cargado.size / 2**20) if cargado else None,
        "version_ollama": cliente._request_raw("GET", "/api/version").json()["version"],
        "digest": cargado.digest if cargado else None, "fecha": datetime.now().isoformat(timespec="seconds"),
    }
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    return registro


def esquema_json(schema: str) -> dict:
    """Esquema JSON de la respuesta: cada campo es {"valor", "evidencia"}; las clases van como enum."""
    esquema = _config()["esquemas"][schema]
    texto = {"type": ["string", "null"]}

    def campo(valor):
        return {"type": "object", "properties": {"valor": valor, "evidencia": texto}, "required": ["valor", "evidencia"]}

    def lista(propiedades, maximo):
        return {"type": "array", "maxItems": maximo,
                "items": {"type": "object", "properties": {**propiedades, "evidencia": {"type": "string"}},
                          "required": [*propiedades, "evidencia"]}}

    llm = _config()["extraccion"]["llm"]

    if schema == "entrevista":
        propiedades = {
            "anios_experiencia": campo({"type": ["number", "null"]}),
            "ultimo_puesto": campo(texto),
            "tecnologias": lista({"valor": {"type": "string"}}, llm["max_tecnologias"]),
            "pretension_salarial": campo({"anyOf": [
                {"type": "object", "properties": {"monto": {"type": "number"}, "moneda": {"enum": esquema["monedas"]}},
                 "required": ["monto", "moneda"]}, {"type": "null"}]}),
            "disponibilidad": campo(texto),
            "nivel_ingles": campo({"enum": [*esquema["clases"]["nivel_ingles"], None]}),
        }
    elif schema == "pedido":
        productos = esquema["productos"]
        propiedades = {
            "items": lista({"producto": {"enum": list(productos)}, "tamano": {"enum": _tamanos()},
                            "cantidad": {"type": "integer"}}, llm["max_items"]),
            "promocion": campo({"enum": [*esquema["alias"]["promocion"], None]}),
            "descuento": campo({"type": "number"}),
            "direccion_entrega": campo(texto),
            "metodo_pago": campo({"enum": [*esquema["clases"]["metodo_pago"], None]}),
            "total_dicho": campo({"type": ["number", "null"]}),
        }
    else:
        raise ValueError(f"esquema desconocido: {schema!r}")
    return {"type": "object", "properties": propiedades, "required": list(propiedades)}


def _mensajes(transcript, schema):
    cfg = _config()
    prompts = cfg["extraccion"]["prompts"]
    usuario = prompts[schema].format(transcript=" ".join(transcript.split()),
                                     fecha_grabacion=cfg["proyecto"]["fecha_grabacion"],
                                     productos=_carta_en_texto())
    return [{"role": "system", "content": prompts["sistema"]}, {"role": "user", "content": usuario}]


def _convertir(campo, dato):
    """La respuesta del modelo para un campo, en la forma de src.extraccion_reglas."""
    if campo == "tecnologias":
        return {"valor": [t["valor"] for t in dato], "evidencia": [t["evidencia"] for t in dato]}
    if campo == "items":
        valor = [{"producto": i["producto"], "tamano": i["tamano"], "cantidad": int(i["cantidad"]),
                  "precio_unitario": precio_carta(i["producto"], i["tamano"])} for i in dato]
        menciones = [i["evidencia"] for i in dato]
        return {"valor": valor or None, "evidencia": " … ".join(menciones) or None, "menciones": menciones}
    valor = dato["valor"]
    if campo in ("anios_experiencia", "descuento", "total_dicho") and valor is not None:
        valor = _numero(valor)
    elif campo == "pretension_salarial" and valor is not None:
        valor = {"monto": _numero(valor["monto"]), "moneda": valor["moneda"]}
    elif campo == "disponibilidad" and valor is not None:
        valor = date.fromisoformat(valor).isoformat()  # una fecha mal formada o inexistente queda como error
    return {"valor": valor, "evidencia": dato["evidencia"]}


def _numero(valor):
    return int(valor) if float(valor).is_integer() else float(valor)


def _tamanos():
    """Etiquetas de tamaño: las de config.yaml y, para los productos sin tamaños, el único de la carta."""
    import pandas as pd

    carta = pd.read_csv(_config()["rutas"]["carta"])
    etiquetas = []
    for producto, datos in _config()["esquemas"]["pedido"]["productos"].items():
        etiquetas += list(datos.get("tamanos") or carta.loc[carta.producto == producto, "tamano"])
    return list(dict.fromkeys(etiquetas))


def _carta_en_texto():
    productos = _config()["esquemas"]["pedido"]["productos"]
    import pandas as pd

    carta = pd.read_csv(_config()["rutas"]["carta"])
    return "; ".join(f"{p} ({', '.join(d.get('tamanos') or carta.loc[carta.producto == p, 'tamano'])})"
                     for p, d in productos.items())


def _ruta_cache(modelo, clave):
    cfg = _config()
    return Path(cfg["rutas"]["cache_dir"]) / cfg["cache"]["patron_llm"].format(modelo=modelo.replace(":", "_"), clave=clave)


@cache
def _config():
    return cargar_config()
