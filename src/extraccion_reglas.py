"""Extracción por reglas (expresiones regulares) para los esquemas de config.yaml.

La entrada es una transcripción sin hablantes ni turnos, como la entrega Whisper. Se parte en
oraciones; cada una se guarda tal cual (para la evidencia) y con los números en dígitos
(src.normalizacion.palabras_a_numeros, para buscar valores). Cada campo devuelve
{"valor": ..., "evidencia": oración original de la que sale}. Los marcadores están en
config.yaml -> extraccion.reglas y el vocabulario en config.yaml -> esquemas y asr.glosario.

Reglas generales
- Pregunta y respuesta: una pregunta se reconoce por sus palabras clave. Su respuesta es la propia
  oración (si no termina en "?") y las siguientes, hasta la próxima pregunta o ventana_respuesta
  oraciones.
- Autocorrección: un valor seguido, en la misma oración, de un marcador de corrección ("no, perdón",
  "me equivoqué") se descarta. Entre los valores que quedan vale el último.

Entrevista
- pretension_salarial: montos >= monto_minimo en la respuesta a la pregunta salarial, sin las
  oraciones de salario actual ("gano", "estoy ganando"). Si una oración dice "idealmente", vale su
  monto; si no, el último. Moneda: un alias en la oración del monto, si no en las demás oraciones de
  la respuesta (primero las anteriores) y si no moneda_por_defecto.
- anios_experiencia: duraciones en la respuesta a la pregunta de experiencia. Se descartan las
  aproximadas ("casi cinco") y las parciales ("los últimos dos"). Vale la última. Si una oración suma
  tramos ("un año y medio en ... y otro año en ..."), se suman. Si solo se dice el año de inicio
  ("desde 2023"), años = año de grabación - año de inicio.
- disponibilidad: en la respuesta a la pregunta de disponibilidad, la última oración con una
  expresión de fecha; ver interpretar_fecha.
- tecnologias: términos de asr.glosario.tecnologias en todo el texto, en orden de aparición. Un término
  se excluye solo si todas sus menciones están en oraciones con un marcador de abandono ("lo apagamos")
  y sin marcador de continuidad ("todavía mantenemos").
- nivel_ingles: la última palabra de nivel en la respuesta a la pregunta por el inglés; si no hay, el
  último código MCER (C1 -> avanzado). Sin pregunta reconocible, se busca en todo el texto.
- ultimo_puesto: frase que empieza en un cargo (lista cargos) y llega hasta una palabra de corte o un
  signo de puntuación. Se descartan los cargos pasados ("empecé como") y los ofrecidos ("buscamos").
  Vale la frase más larga, que es la más específica.

Pedido
- items: la fuente principal es la última confirmación del vendedor ("le confirmo", "le repito"), que ya
  contiene el pedido corregido; el diálogo, en cambio, trae cada versión intermedia. Solo si no hay
  confirmación se recorre el diálogo: cada mención de cantidad + producto actualiza el pedido,
  "en vez de" quita lo que sigue y una corrección deja solo lo dicho después del marcador.
- precio_unitario: sale de carta.csv, nunca del audio, porque varios precios no se dicen.
- promocion y descuento: la última mención de un alias de promoción; el descuento sale de promociones.csv.
  Si no hay ninguna, se busca una respuesta negativa a la pregunta por la promoción ("¿Tiene algún
  código?" -> "No, ninguno."): el valor queda nulo (descuento 0) y esa respuesta es la evidencia de
  que la ausencia se dijo. Si tampoco la hay, el campo queda nulo y sin evidencia.
- direccion_entrega: la última dirección con tipo de vía y número (la corregida, si hubo corrección);
  si esa mención no trae distrito, se toma de otra mención de la misma vía.
- metodo_pago: el primer alias en la respuesta a la pregunta de pago; si no hay, el último del texto.
- total_dicho: el último número después de "total".

Fechas (interpretar_fecha), de la más específica a la menos
1. Día y mes: "primero de diciembre", "11 de enero", "enero, el lunes 11". Es la próxima fecha con ese
   día y mes desde la grabación: enero, dicho en octubre, es del año siguiente.
2. Relativa: "en 2 semanas", "dentro de 3 días", "un mes de preaviso". Se suma a la fecha de grabación.
   Un mes es un mes de calendario; si el día no existe en el mes de destino se usa su último día:
   31 de octubre + 1 mes = 30 de noviembre.
3. "fin de mes": último día del mes de grabación.
4. Mes solo, con preposición ("a partir de enero"): día 1 del próximo mes con ese nombre.
5. Inmediata ("de inmediato"): la fecha de grabación.
"""

import calendar
import re
from datetime import date, timedelta
from functools import cache

import pandas as pd

from src.config import cargar_config
from src.normalizacion import normalizar_texto, palabras_a_numeros

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

_NUMERO = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?!\w|\.\d)")
_CANTIDAD = re.compile(r"(?<![\w.])(\d+|un|una|unos|unas)(?!\w)", re.IGNORECASE)


def extraer(transcript: str, schema: str) -> dict:
    """Extrae los campos del esquema con expresiones regulares.

    Returns:
        dict campo -> {"valor": ..., "evidencia": oración de la transcripción o None}.
    """
    reglas = _config()["extraccion"]["reglas"]
    oraciones = _oraciones(transcript)
    if schema == "entrevista":
        e = reglas["entrevista"]
        return {
            "anios_experiencia": _experiencia(oraciones, e),
            "ultimo_puesto": _puesto(oraciones, e),
            "tecnologias": _tecnologias(oraciones, e),
            "pretension_salarial": _pretension(oraciones, e, reglas["correccion"]),
            "disponibilidad": _disponibilidad(oraciones, e),
            "nivel_ingles": _nivel_ingles(oraciones, e),
        }
    if schema == "pedido":
        p = reglas["pedido"]
        promocion, descuento = _promocion(oraciones, p, reglas["negacion"])
        return {
            "items": _items(oraciones, p, reglas["correccion"]),
            "promocion": promocion,
            "descuento": descuento,
            "direccion_entrega": _direccion(oraciones, p),
            "metodo_pago": _metodo_pago(oraciones, p),
            "total_dicho": _total(oraciones),
        }
    raise ValueError(f"esquema desconocido: {schema!r}")


def interpretar_fecha(texto: str, fecha_base: date | None = None) -> tuple[str, date] | None:
    """Busca en una oración (con números en dígitos) su expresión de fecha más específica.

    Returns:
        (expresión tal como aparece en el texto, fecha absoluta), o None si no hay ninguna.
    """
    base = fecha_base or date.fromisoformat(_config()["proyecto"]["fecha_grabacion"])
    meses = "|".join(MESES)
    dias = "|".join(DIAS_SEMANA)

    def ultimo(patron):
        coincidencias = list(re.finditer(patron, texto, re.IGNORECASE))
        return coincidencias[-1] if coincidencias else None

    m = ultimo(rf"(?:(?:{dias})\s+)?(\d{{1,2}}|primero)\s+de\s+({meses})\b")
    if m:
        fecha = _proxima(base, MESES.index(m[2].lower()) + 1, _dia(m[1]))
        if fecha:
            return m[0], fecha
    m = ultimo(rf"\b({meses})\b[^.?!]*?\bel\s+(?:(?:{dias})\s+)?(\d{{1,2}}|primero)\b")
    if m:
        fecha = _proxima(base, MESES.index(m[1].lower()) + 1, _dia(m[2]))
        if fecha:
            return m[0], fecha
    unidad = r"(días?|semanas?|mes(?:es)?)"
    m = ultimo(rf"\b(?:en|dentro\s+de)\s+(?:unas?\s+|unos\s+)?(\d+|un|una)\s+{unidad}\b") or ultimo(
        rf"(?<!\w)(\d+|un|una)\s+{unidad}\s+de\s+preaviso\b")
    if m:
        n = int(m[1]) if m[1].isdigit() else 1
        if m[2].lower().startswith("mes"):
            return m[0], _sumar_meses(base, n)
        return m[0], base + timedelta(days=n * (7 if m[2].lower().startswith("semana") else 1))
    m = ultimo(r"\bfin(?:es)?\s+de\s+mes\b")
    if m:
        return m[0], base.replace(day=calendar.monthrange(base.year, base.month)[1])
    m = ultimo(rf"\b(?:en|a\s+partir\s+de|desde)\s+({meses})\b")
    if m:
        return m[0], _proxima(base, MESES.index(m[1].lower()) + 1, 1)
    m = ultimo(_patron(_config()["extraccion"]["reglas"]["entrevista"]["inmediato"]))
    if m:
        return m[0], base
    return None


# --- Entrevista -------------------------------------------------------------------------------

def _pretension(oraciones, e, correccion):
    esquema = _config()["esquemas"]["entrevista"]
    indices = _respuesta(oraciones, e["pregunta_pretension"])
    candidatos = []
    for i in indices:
        original, conv = oraciones[i]
        if _contiene(original, e["salario_actual"]):
            continue
        for m in _NUMERO.finditer(conv):
            if float(m[1]) >= e["monto_minimo"] and not _contiene(conv[m.end():], correccion):
                candidatos.append((i, float(m[1]), _contiene(original, e["ideal"])))
    if not candidatos:
        return _vacio()
    i, monto, _ = ([c for c in candidatos if c[2]] or candidatos)[-1]
    orden = [i] + [j for j in reversed(indices) if j < i] + [j for j in indices if j > i]
    moneda = next((cod for j in orden for cod, alias in esquema["alias"]["moneda"].items()
                   if _contiene(oraciones[j][0], alias)), esquema["moneda_por_defecto"])
    return _campo({"monto": _numero(monto), "moneda": moneda}, oraciones[i][0])


def _experiencia(oraciones, e):
    anio_grabacion = date.fromisoformat(_config()["proyecto"]["fecha_grabacion"]).year
    adicional = _patron(e["adicional"])
    duraciones, inicios = [], []
    for i in _respuesta(oraciones, e["pregunta_experiencia"]):
        conv = oraciones[i][1]
        tramos = []
        for m in _NUMERO.finditer(conv):
            valor, antes, despues = float(m[1]), conv[: m.start()], conv[m.end():]
            if 1900 <= valor <= anio_grabacion:
                inicios.append((i, valor))
            elif (valor <= e["anios_maximo"]
                  and not re.search(rf"(?:{_patron(e['aproximacion'])}|{_patron(e['subconjunto'])}"
                                    rf"|{adicional})\s*$", antes, re.IGNORECASE)
                  and not re.match(r"\s*(?:%|por ciento|mes|meses|semanas?|días?)\b", despues, re.IGNORECASE)):
                tramos.append(valor)
        extra = [float(m[1]) if m[1] else 1.0 for m in
                 re.finditer(rf"{adicional}\s+(?:(\d+(?:\.\d+)?)\s+)?años?\b", conv, re.IGNORECASE)]
        if extra:
            duraciones.append((i, sum(tramos) + sum(extra)))
        else:
            duraciones += [(i, t) for t in tramos]
    if duraciones:
        i, valor = duraciones[-1]
    elif inicios:
        i, inicio = inicios[-1]
        valor = anio_grabacion - inicio
    else:
        return _vacio()
    return _campo(_numero(valor), oraciones[i][0])


def _disponibilidad(oraciones, e):
    for i in reversed(_respuesta(oraciones, e["pregunta_disponibilidad"])):
        encontrada = interpretar_fecha(oraciones[i][1])
        if encontrada:
            return _campo(encontrada[1].isoformat(), oraciones[i][0])
    return _vacio()


def _tecnologias(oraciones, e):
    normalizadas = [normalizar_texto(original) for original, _ in oraciones]
    encontradas = []
    for termino in _config()["asr"]["glosario"]["tecnologias"]:
        patron = rf"(?<!\w){re.escape(normalizar_texto(termino))}(?!\w)"
        for i, texto in enumerate(normalizadas):
            m = re.search(patron, texto)
            original = oraciones[i][0]
            if m and not (_contiene(original, e["abandono"]) and not _contiene(original, e["continua"])):
                encontradas.append(((i, m.start()), termino, original))
                break
    encontradas.sort()
    return {"valor": [t for _, t, _ in encontradas], "evidencia": [o for _, _, o in encontradas]}


def _nivel_ingles(oraciones, e):
    esquema = _config()["esquemas"]["entrevista"]
    indices = _respuesta(oraciones, e["pregunta_ingles"]) or range(len(oraciones))
    palabras, codigos = [], []
    for i in indices:
        original = oraciones[i][0]
        for clase, alias in esquema["alias"]["nivel_ingles"].items():
            palabras += [((i, m.start()), clase) for m in re.finditer(_patron(alias), original, re.IGNORECASE)]
        codigos += [((i, m.start()), esquema["mcer"][m[0].upper()])
                    for m in re.finditer(_patron(list(esquema["mcer"])), original, re.IGNORECASE)]
    elegidos = sorted(palabras) or sorted(codigos)
    if not elegidos:
        return _vacio()
    (i, _), clase = elegidos[-1]
    return _campo(clase, oraciones[i][0])


def _puesto(oraciones, e):
    fin = {p.lower() for p in e["cargo_fin"]}
    candidatos = []
    for original, _ in oraciones:
        for m in re.finditer(_patron(e["cargos"]), original, re.IGNORECASE):
            antes = original[: m.start()]
            if _contiene(antes, e["cargo_pasado"]) or _contiene(antes, e["cargo_ofrecido"]):
                continue
            palabras = [m[0]]
            for siguiente in re.match(r"(?:\s+[^\W_]+)*", original[m.end():])[0].split():
                if siguiente.lower() in fin or len(palabras) >= e["cargo_max_palabras"]:
                    break
                palabras.append(siguiente)
            while palabras[-1].lower() in {"de", "del", "la", "las", "los", "el"}:
                palabras.pop()
            candidatos.append((len(palabras), " ".join(palabras), original))
    if not candidatos:
        return _vacio()
    _, frase, original = max(enumerate(candidatos), key=lambda x: (x[1][0], x[0]))[1]
    return _campo(frase[0].upper() + frase[1:], original)


# --- Pedido -----------------------------------------------------------------------------------

def _items(oraciones, p, correccion):
    confirmaciones = [i for i, (original, _) in enumerate(oraciones) if _contiene(original, p["confirmacion"])]
    if confirmaciones:
        original, conv = oraciones[confirmaciones[-1]]
        segmento = conv[re.search(_patron(p["confirmacion"]), conv, re.IGNORECASE).end():]
        menciones = [(t, item) for t in _trozos(segmento) if (item := interpretar_item(t))]
        if menciones:
            return {"valor": [item for _, item in menciones], "evidencia": original,
                    "menciones": [t for t, _ in menciones], "fuente": "confirmacion"}
    return _items_dialogo(oraciones, p, correccion)


def _items_dialogo(oraciones, p, correccion):
    pedido, menciones, evidencias = {}, {}, []
    for original, conv in oraciones:
        texto = conv
        marcas = list(re.finditer(_patron(correccion), texto, re.IGNORECASE))
        if marcas and any(interpretar_item(t) for t in _trozos(texto[marcas[-1].end():])):
            texto = texto[marcas[-1].end():]
        agregar, *quitar = re.split(_patron(p["reemplazo"]), texto, maxsplit=1, flags=re.IGNORECASE)
        cambio = False
        for trozo in _trozos(quitar[0] if quitar else ""):
            for clave in [c for c in pedido if _menciona(trozo, *c)]:
                del pedido[clave]
                cambio = True
        for trozo in _trozos(agregar):
            if item := interpretar_item(trozo):
                clave = (item["producto"], item["tamano"])
                pedido[clave], menciones[clave] = item, trozo
                cambio = True
        if cambio:
            evidencias.append(original)
    if not pedido:
        return _vacio()
    return {"valor": list(pedido.values()), "evidencia": " … ".join(evidencias),
            "menciones": [menciones[c] for c in pedido], "fuente": "dialogo"}


def interpretar_item(trozo: str) -> dict | None:
    """Cantidad + producto + tamaño de un trozo de texto, con el precio de la carta; None si no hay."""
    cantidad = _CANTIDAD.search(trozo)
    productos = _config()["esquemas"]["pedido"]["productos"]
    encontrados = [(m.start(), nombre) for nombre, datos in productos.items()
                   if (m := re.search(_patron(datos["alias"]), trozo, re.IGNORECASE))]
    if not cantidad or not encontrados:
        return None
    producto = min(encontrados)[1]
    tamanos = productos[producto].get("tamanos", {})
    tamano = next((etiqueta for etiqueta, alias in tamanos.items() if _contiene(trozo, alias)), None)
    carta = _carta()[lambda c: c.producto == producto]
    if tamano is None and len(tamanos) == 1:
        tamano = next(iter(tamanos))
    elif tamano is None and not tamanos and len(carta) == 1:
        tamano = carta.tamano.iloc[0]
    return {"producto": producto, "tamano": tamano,
            "cantidad": int(cantidad[1]) if cantidad[1].isdigit() else 1,
            "precio_unitario": precio_carta(producto, tamano)}


def precio_carta(producto: str, tamano: str | None) -> int | None:
    """Precio en carta.csv; el tamaño es una etiqueta con la que empieza el de la carta ("jarra")."""
    carta = _carta()[lambda c: c.producto == producto]
    fila = carta[carta.tamano.str.startswith(tamano)] if tamano else carta.iloc[0:0]
    return int(fila.precio.iloc[0]) if len(fila) == 1 else None


def _menciona(trozo, producto, tamano):
    datos = _config()["esquemas"]["pedido"]["productos"][producto]
    return _contiene(trozo, datos["alias"]) or (tamano in datos.get("tamanos", {})
                                                and _contiene(trozo, datos["tamanos"][tamano]))


def _trozos(texto):
    partes = re.split(r"[,;:…]\s*|\s+y\s+(?=(?:un|una|unos|unas|\d+)\b)", texto, flags=re.IGNORECASE)
    return [t.strip(" .¿?¡!") for t in partes if t.strip(" .¿?¡!")]


def _promocion(oraciones, p, negacion):
    alias = _config()["esquemas"]["pedido"]["alias"]["promocion"]
    # Se busca en la versión con dígitos: el alias "LEÑA5" solo existe después de convertir "LEÑA cinco".
    menciones = [((i, m.start()), nombre, original) for i, (original, conv) in enumerate(oraciones)
                 for nombre, frases in alias.items()
                 for m in re.finditer(_patron(frases), conv, re.IGNORECASE)]
    if not menciones:
        for i in _respuesta(oraciones, p["pregunta_promocion"]):
            if re.match(_patron(negacion), oraciones[i][0].lstrip("¿¡ "), re.IGNORECASE):
                return _campo(None, oraciones[i][0]), _campo(0, oraciones[i][0])
        return _vacio(), _campo(0, None)
    _, nombre, original = max(menciones)
    promociones = pd.read_csv(_config()["rutas"]["promociones"]).set_index("promocion")
    return _campo(nombre, original), _campo(int(promociones.descuento[nombre]), original)


def _direccion(oraciones, p):
    via, comp = _patron(p["tipos_via"]), _patron(p["complementos_direccion"])
    mayuscula = r"[A-ZÁÉÍÓÚÑ][^\W\d_]*"
    patron = re.compile(
        rf"(?i:({via}))\.?\s+((?:[^\W\d_]+\s+){{1,5}}?)(\d+)"
        rf"((?:,?\s*(?i:{comp})\s+[^\W_]+)*)"
        rf"(?:,?\s*en\s+({mayuscula}(?:\s+(?:de|del|la|las|los|{mayuscula}))*))?"
    )
    menciones = [(m, original) for original, conv in oraciones for m in patron.finditer(conv)]
    if not menciones:
        return _vacio()
    m, original = menciones[-1]
    calle = f"{m[1]} {m[2].strip()}"
    distrito = m[5] or next((o[5] for o, _ in reversed(menciones)
                             if o[5] and f"{o[1]} {o[2].strip()}".lower() == calle.lower()), None)
    partes = [f"{calle} {m[3]}"]
    partes += [f"{t} {v}" for t, v in re.findall(rf"(?i:({comp}))\s+([^\W_]+)", m[4])]
    partes += [distrito] if distrito else []
    return _campo(", ".join(partes), original)


def _metodo_pago(oraciones, p):
    alias = _config()["esquemas"]["pedido"]["alias"]["metodo_pago"]

    def menciones(indices):
        return sorted(((i, m.start()), metodo, oraciones[i][0]) for i in indices
                      for metodo, frases in alias.items()
                      for m in re.finditer(_patron(frases), oraciones[i][0], re.IGNORECASE))

    en_respuesta = menciones(_respuesta(oraciones, p["pregunta_pago"]))
    elegida = en_respuesta[0] if en_respuesta else (menciones(range(len(oraciones))) or [None])[-1]
    return _campo(elegida[1], elegida[2]) if elegida else _vacio()


def _total(oraciones):
    menciones = [(int(m[1]), original) for original, conv in oraciones
                 for m in re.finditer(r"(?<!\w)total(?!\w)[^.?!\d]*?(\d+)", conv, re.IGNORECASE)]
    return _campo(*menciones[-1]) if menciones else _vacio()


# --- Utilidades -------------------------------------------------------------------------------

@cache
def _config() -> dict:
    return cargar_config()


@cache
def _carta() -> pd.DataFrame:
    return pd.read_csv(_config()["rutas"]["carta"])


def _oraciones(transcript):
    """(original, con números en dígitos) por oración. Los puntos suspensivos no cortan la oración."""
    texto = " ".join(transcript.split())
    return [(o, palabras_a_numeros(o)) for o in re.split(r"(?<=[.!?])(?<!\.\.\.)\s+", texto) if o]


def _respuesta(oraciones, claves):
    ventana = _config()["extraccion"]["reglas"]["ventana_respuesta"]
    indices = []
    for i, (original, _) in enumerate(oraciones):
        if not _contiene(original, claves):
            continue
        tramo = [] if _es_pregunta(original) else [i]
        for j in range(i + 1, min(i + 1 + ventana, len(oraciones))):
            if _es_pregunta(oraciones[j][0]):
                break
            tramo.append(j)
        indices += [k for k in tramo if k not in indices]
    return sorted(indices)


def _es_pregunta(oracion):
    return oracion.rstrip().endswith("?")


def _patron(frases):
    return r"(?<!\w)(?:" + "|".join(re.escape(f) for f in sorted(frases, key=len, reverse=True)) + r")(?!\w)"


def _contiene(texto, frases):
    return re.search(_patron(frases), texto, re.IGNORECASE) is not None


def _dia(texto):
    return 1 if texto.lower() == "primero" else int(texto)


def _proxima(base, mes, dia):
    """La próxima fecha (desde base, inclusive) con ese día y mes; None si el día no existe."""
    for anio in (base.year, base.year + 1):
        try:
            fecha = date(anio, mes, dia)
        except ValueError:
            return None
        if fecha >= base:
            return fecha
    return None


def _sumar_meses(base, meses):
    anio, mes = divmod(base.month - 1 + meses, 12)
    anio, mes = base.year + anio, mes + 1
    return date(anio, mes, min(base.day, calendar.monthrange(anio, mes)[1]))


def _numero(valor):
    return int(valor) if float(valor).is_integer() else float(valor)


def _campo(valor, evidencia):
    return {"valor": valor, "evidencia": evidencia}


def _vacio():
    return _campo(None, None)
