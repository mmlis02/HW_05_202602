"""Normalización de texto y de números dichos en palabras.

Todos los parámetros viven en config.yaml -> normalizacion. Las dos funciones aceptan `reglas`
para probar otra configuración sin editar el archivo.

palabras_a_numeros(texto): números en palabras a dígitos dentro de texto corrido.
    1. Alias. Formas que text2num no reconoce se reescriben antes: "veintiún" -> "veintiuno"
       (apócope) y "veintitres" -> "veintitrés". Así "ciento veintiún soles" llega a 121.
    2. Palabras protegidas. Los ordinales ("cuarto", "segunda", "primero") y "por ciento" se apartan
       y vuelven intactos. Sin esto, "tres cuartos de pollo" sale "3 4ᵒˢ de pollo".
    3. Artículos. "un", "una", "uno", "unos" y "unas" se apartan como en el paso 2, salvo cuando son
       parte de un número: detrás de otra palabra numérica ("ciento un" -> 101, "tres dos uno" -> 321)
       o detrás de "decena y" ("treinta y un" -> 31). Detrás de "seis y" es un artículo:
       "treinta y seis y una ensalada" -> "36 y una ensalada". El umbral del paso 4 no basta, porque
       text2num convierte el artículo cuando va junto a otro número: "casi un quince por ciento"
       saldría "casi 1 15" y "unos cuarenta minutos", "1 40".
    4. Conversión con text2num.alpha2digit(texto, "es", threshold=umbral_numeros_pequenos).
       Con umbral 2 se convierte desde "dos" ("dos jarras" -> "2 jarras") y "cero" suelto queda en
       palabra. Que "un pollo" signifique cantidad 1 lo decide la extracción, que sabe que va delante
       de un producto de la carta.
    5. "y medio". Solo tras número + unidad de tiempo (unidades_y_medio):
       "cuatro años y medio" -> "4.5 años", "un año y medio" -> "1.5 año". En "medio pollo" y
       "litro y medio", "medio" es un tamaño y no se toca.
    6. Dictado. Una corrida de al menos min_digitos_dictado dígitos sueltos se une en un número:
       "nueve ocho siete, seis cinco cuatro" -> "987, 654". Las comas separan los grupos.
    7. Códigos. Las letras de un código seguidas de su número se unen: "LEÑA cinco" -> "LEÑA5".
    Una autocorrección ("mil cuarenta y tres… no, es mil treinta y cuatro") deja los dos números:
    elegir el final es trabajo de la extracción.

normalizar_texto(texto): la regla única para comparar referencia y transcripción.
    1. palabras_a_numeros, antes de quitar la puntuación (las comas separan grupos de un dictado).
    2. "%" -> " por ciento", para que "15%" y "quince por ciento" queden iguales.
    3. Minúsculas.
    4. Formato de cifras: el separador de miles se quita ("6.500" -> "6500") y la coma decimal pasa a
       punto ("4,5" -> "4.5"). Un punto o coma seguido de exactamente tres dígitos es de miles.
    5. Tildes: se mantienen (quitar_tildes: false). Con true se quitan á é í ó ú ü, pero no la ñ.
    6. Puntuación: se reemplaza por espacio, salvo el punto decimal entre dígitos.
    7. Espacios colapsados.
"""

import re
import unicodedata
from functools import cache

from text_to_num import alpha2digit, text2num

from src.config import cargar_config


@cache
def _reglas_config() -> dict:
    return cargar_config()["normalizacion"]


def palabras_a_numeros(texto: str, reglas: dict | None = None) -> str:
    """Convierte números dichos en palabras a dígitos dentro de texto corrido.

    "mi pretensión es seis mil quinientos soles" -> "mi pretensión es 6500 soles".
    """
    r = reglas or _reglas_config()
    for forma, canonica in r["alias"].items():
        texto = re.sub(rf"\b{re.escape(forma)}\b", canonica, texto, flags=re.IGNORECASE)
    texto, apartadas = _proteger(texto, r["palabras_protegidas"], r["articulos"])
    texto = alpha2digit(texto, "es", threshold=r["umbral_numeros_pequenos"])
    texto = _restaurar(texto, apartadas)
    texto = _y_medio(texto, r["unidades_y_medio"])
    texto = _unir_dictado(texto, r["min_digitos_dictado"])
    return _unir_codigos(texto, r["codigos"])


def normalizar_texto(texto: str, reglas: dict | None = None) -> str:
    """Regla única para comparar referencia y transcripción (WER, CER y verificación literal)."""
    r = reglas or _reglas_config()
    if r["palabras_a_numeros"]:
        texto = palabras_a_numeros(texto, r)
    texto = texto.replace("%", " por ciento")
    if r["minusculas"]:
        texto = texto.lower()
    texto = re.sub(r"(?<=\d)[.,](?=\d{3}(?!\d))", "", texto)
    texto = re.sub(r"(?<=\d),(?=\d)", ".", texto)
    if r["quitar_tildes"]:
        texto = _quitar_tildes(texto)
    if r["quitar_puntuacion"]:
        texto = re.sub(r"[^\w\s.]|_", " ", texto)
        texto = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", texto)
    if r["colapsar_espacios"]:
        texto = " ".join(texto.split())
    return texto


def _proteger(texto: str, palabras: list[str], articulos: list[str]) -> tuple[str, list[str]]:
    """Reemplaza palabras protegidas y artículos por marcas que text2num no puede leer como número."""
    apartadas = []

    def marcar(m):
        apartadas.append(m[0])
        return f"⟦{len(apartadas) - 1}⟧"

    def marcar_articulo(m):
        antes = re.findall(r"\w+", m.string[: m.start()])[-2:]
        if antes and _valor(antes[-1]) is not None:
            return m[0]
        if len(antes) == 2 and antes[1].lower() == "y" and _valor(antes[0]) in range(30, 100, 10):
            return m[0]
        return marcar(m)

    patron = "|".join(re.escape(p) for p in sorted(palabras, key=len, reverse=True))
    texto = re.sub(rf"\b(?:{patron})s?\b", marcar, texto, flags=re.IGNORECASE)
    patron = "|".join(re.escape(a) for a in sorted(articulos, key=len, reverse=True))
    texto = re.sub(rf"\b(?:{patron})\b", marcar_articulo, texto, flags=re.IGNORECASE)
    return texto, apartadas


def _valor(palabra: str) -> int | None:
    """Valor de una palabra numérica suelta ("treinta" -> 30), o None si no es un número."""
    if palabra.isdigit():
        return int(palabra)
    try:
        return text2num(palabra.lower(), "es")
    except ValueError:
        return None


def _restaurar(texto: str, apartadas: list[str]) -> str:
    return re.sub(r"⟦(\d+)⟧", lambda m: apartadas[int(m[1])], texto)


def _y_medio(texto: str, unidades: list[str]) -> str:
    patron = "|".join(re.escape(u) for u in unidades)
    return re.sub(
        rf"\b(\d+|un|una)\s+({patron})\s+y\s+medi[oa]\b",
        lambda m: f"{int(m[1]) if m[1].isdigit() else 1}.5 {m[2]}",
        texto,
        flags=re.IGNORECASE,
    )


def _unir_dictado(texto: str, minimo: int) -> str:
    return re.sub(rf"\b\d(?: \d){{{minimo - 1},}}\b", lambda m: m[0].replace(" ", ""), texto)


def _unir_codigos(texto: str, codigos: list[str]) -> str:
    for codigo in codigos:
        letras, numero = re.fullmatch(r"(\D+?)(\d+)", codigo).groups()
        texto = re.sub(rf"\b{re.escape(letras)}\s*{numero}\b", codigo, texto, flags=re.IGNORECASE)
    return texto


def _quitar_tildes(texto: str) -> str:
    """Quita acento agudo, grave y diéresis; conserva la virgulilla de la ñ."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return unicodedata.normalize("NFC", re.sub("[̀́̈]", "", descompuesto))
