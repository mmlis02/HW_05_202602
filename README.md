# De la voz al registro — Entrevistas y llamadas de venta

Proyecto integrador de ASR: una entrevista grabada se convierte en una ficha de candidato (Task 1) y una llamada de venta en un pedido que se verifica a sí mismo (Task 2), con un solo motor para las dos.

## Setup

### GPU en un sistema sin CUDA 12 (Colab)

- **Problema.** Colab pasó a Python 3.13 con una CUDA más nueva y ya no trae las librerías de CUDA 12. CTranslate2 4.x, el motor de faster-whisper, necesita cuBLAS para CUDA 12 y cuDNN 9. La GPU se detecta igual, pero al transcribir falla con `RuntimeError: Library libcublas.so.12 is not found or cannot be loaded`.
- **Solución.** `pip install -r requirements-gpu.txt` instala `nvidia-cublas-cu12==12.9.1.4` y `nvidia-cudnn-cu12==9.10.2.21`, como indica la documentación de faster-whisper 1.2.1. Después, `src.transcripcion.precargar_cuda12()` las carga en el proceso con `ctypes` y `RTLD_GLOBAL`, en orden (`libcublasLt` antes que `libcublas`, y las subbibliotecas de cuDNN antes que `libcudnn`). Cuando CTranslate2 pide `libcublas.so.12`, la encuentra ya cargada. `cargar_modelo` llama a esa función cada vez que el device es `cuda`.
- **Por qué no `LD_LIBRARY_PATH`.** El cargador del sistema solo la lee al arrancar el proceso. Cambiarla con el kernel ya iniciado no tiene efecto, y en Colab tampoco sobrevive a un reinicio de la sesión.
- **Comprobación.** `notebooks/02_transcripcion_gpu.ipynb` transcribe, justo después de instalar, un segundo de silencio con el modelo `tiny` en `cuda`. Si las librerías fallan, falla ahí y no a mitad de la corrida.
- **PyAV.** `av` está fijado en 18.1.0: faster-whisper 1.2.1 usa un argumento de `av.open` que PyAV 19 eliminó, y sin esa versión toda lectura de audio falla.

## Audios

Los 10 audios del corpus (5 entrevistas y 5 llamadas) **no están en este repositorio ni en su historial, por privacidad**. Todo lo que se dice en ellos es inventado, pero son voces de personas reales. Están en una carpeta privada de Google Drive, y el enlace a esa carpeta tampoco se publica.

- **Cómo pedirlos:** abre un issue en este repositorio pidiendo acceso e indica la cuenta de Google con la que quieres verlos. La carpeta se comparte con esa cuenta, con permiso de lectura.
- **Nombres:** los archivos conservan su nombre original: `task 1-1` … `task 1-5` (entrevistas E1 a E5) y `task 2-1` … `task 2-5` (llamadas L1 a L5). La extensión puede variar. El mapeo a los clips `e1 … l5` está en `config.yaml → audios.archivos`.
- **En Colab:** `notebooks/02_transcripcion_gpu.ipynb` monta Drive y busca esos 10 archivos dentro de `MyDrive`, en cualquier subcarpeta. Se detiene si falta o se repite alguno, y muestra la carpeta que encontró.
- **Copia local (opcional):** con los nombres originales, en `data/audio/`. `.gitignore` excluye los formatos de audio para que nunca se suban.

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
- **Cifras mixtas**: Whisper escribe "10 mil" donde el guion dice "diez mil"; text2num leía "mil" suelto y daba "10 1000", dos errores de WER por una palabra bien oída. Ahora un multiplicador ("mil", "millón", "millones") detrás de una cifra, de "un", "una" o "medio" se multiplica: "10 mil" → 10000, "1.5 millones" y "1,5 millones" → 1500000, "medio millón" → 500000, "un millón y medio" → 1500000. Una cifra menor que el multiplicador justo detrás se suma: "10 mil 500" → 10500, "2 millones 500 mil" → 2500000.
- **Códigos**: "LEÑA cinco" → LEÑA5.
- **Autocorrecciones**: se convierten los dos números; elegir el final es trabajo de la extracción.
- **Para comparar textos** (WER, CER, verificación): números a dígitos, `%` → "por ciento", minúsculas, separador de miles fuera y coma decimal a punto, sin puntuación (salvo el punto decimal), espacios colapsados. Las tildes se mantienen (`quitar_tildes: false`).
- **Limitaciones**: "entre nueve y diez mil" da 9 y 10000, no 9000; "año y medio" sin número delante no llega a 1.5; un teléfono escrito sin espacios no coincide con el dictado por grupos; una cifra pequeña justo detrás de "mil" se suma aunque no sea parte del número ("10 mil 2 veces" → 10002 veces).

## Diagnóstico de un total que no cuadra

`src/validacion.py`; parámetros en `config.yaml → validacion`; pruebas en `notebooks/05_validacion.ipynb`.

- **Chequeo:** Σ cantidad × precio de la carta − descuento contra el total dicho.
- **Explicación:** una causa de un solo paso que dé la diferencia exacta. Las humanas son descuento olvidado o duplicado, unidad o ítem omitido o de más, y tamaño cobrado por otro. Un salto de ±1, ±10 o ±100 es ambiguo: puede ser una suma mal llevada o un número mal oído.
- **Señal de ASR:** alguna palabra numérica del total o de los ítems tiene `word.probability` menor que 0.6 (provisional).
- **Señales de hablante:** el total se dice dos veces igual, o hay una explicación humana.
- **Decisión:** solo señal de ASR → `asr`; señales de los dos lados → `indeterminado`; solo de hablante → `hablante`; ninguna → `indeterminado`.
- **Sin probabilidades** (transcripciones de referencia), la regla solo puede concluir `hablante` o `indeterminado`.

## Resultados Task 1

## Resultados Task 2

## Herramientas de IA y MCP

## Consentimiento y datos inventados

## Limitaciones
