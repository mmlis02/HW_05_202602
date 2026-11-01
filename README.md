# De la voz al registro — Entrevistas y llamadas de venta

Proyecto integrador de ASR: una entrevista grabada se convierte en una ficha de candidato (Task 1) y una llamada de venta en un pedido que se verifica a sí mismo (Task 2), con un solo motor para las dos.

## Setup

## Comandos

Verificar que el motor no importa librerías de UI. Revisa también las importaciones transitivas, no solo el texto de `engine.py`:

```bash
python -c "import sys, src.engine; ui = {'streamlit','gradio','tkinter','PyQt5','PyQt6','PySide6','dash','flask'}; malas = ui & {m.split('.')[0] for m in sys.modules}; assert not malas, malas; print('OK: src.engine no importa librerías de UI')"
```

## Orden de los notebooks

## Pipeline

## Normalización de números

`src/normalizacion.py`; parámetros en `config.yaml → normalizacion`; casos probados en `notebooks/03_extraccion.ipynb`, sección 1.

- **Palabras a dígitos** en texto corrido con `text2num`: "seis mil quinientos" → 6500, "doscientos cuarenta y cinco" → 245.
- **Artículos**: "un", "una", "uno", "unos" y "unas" no se convierten salvo dentro de un número ("treinta y un" → 31, "ciento un" → 101). "un pollo" queda igual; que sea cantidad 1 lo decide la extracción.
- **Desde "dos"** todo se convierte ("dos jarras" → 2 jarras).
- **Apócope y tildes**: "veintiún" → 21 y "veintitres" sin tilde → 23.
- **Ordinales y "por ciento"** no se convierten: "tres cuartos de pollo" → 3 cuartos, "primero de diciembre" igual.
- **"y medio"** solo tras número + unidad de tiempo: "cuatro años y medio" → 4.5 años. "medio pollo" y "litro y medio" son tamaños y no se tocan.
- **Dictados**: tres o más dígitos sueltos seguidos se unen ("nueve ocho siete" → 987).
- **Códigos**: "LEÑA cinco" → LEÑA5.
- **Autocorrecciones**: se convierten los dos números; elegir el final es trabajo de la extracción.
- **Para comparar textos** (WER, CER, verificación): números a dígitos, `%` → "por ciento", minúsculas, separador de miles fuera y coma decimal a punto, sin puntuación (salvo el punto decimal), espacios colapsados. Las tildes se mantienen (`quitar_tildes: false`).
- **Limitaciones**: "entre nueve y diez mil" da 9 y 10000, no 9000; "año y medio" sin número delante no llega a 1.5; un teléfono escrito sin espacios no coincide con el dictado por grupos.

## Resultados Task 1

## Resultados Task 2

## Herramientas de IA y MCP

## Consentimiento y datos inventados

## Limitaciones
