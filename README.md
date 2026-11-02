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
- **Duraciones:** medidas desde cada archivo en `notebooks/02_transcripcion_gpu.ipynb` (sección 2) y guardadas en `data/resultados/duraciones.csv`. Los 10 clips suman 21.7 min y van de 1.97 a 2.38 min.
- **Desviación conocida: E3 dura 1.97 min (118.4 s).** Le faltan 1.6 s para el mínimo de 2 minutos (`proyecto.duracion_clip_min`), un 1.4 % de ese mínimo. No se regrabó por tres razones:
  - El guion de E3 se grabó completo, tal como está en `docs/guiones.md`, con todos sus campos y trampas.
  - Regrabar obligaría a repetir las 7 corridas de E3 en Colab. Esas corridas ya son la evidencia de la caché, de las mediciones y del notebook 02.
  - Alargarlo 1.6 s no cambia ninguna conclusión.

  El notebook 01 lo marca con `en_rango = False`.

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

## Glosario de transcripción

`config.yaml → asr.glosario_mecanismo: hotwords`; los términos están en `asr.glosario` (tecnologías y restaurante). Medido en `notebooks/02_transcripcion_gpu.ipynb` (sección 8) y recalculado desde la caché en `notebooks/06_resultados.ipynb` (sección 1.7).

- **Qué hace cada mecanismo** en faster-whisper 1.2.1: `initial_prompt` es contexto solo para la primera ventana de 30 s y después se diluye; `hotwords` se antepone al prompt de cada ventana.
- **Resultado** (`large-v3` float16, 10 clips):

  | Mecanismo | WER del corpus | Diferencia media por clip (IC 95 % pareado) | Términos bien transcritos |
  |---|---|---|---|
  | sin glosario | 3.56 % | — | 39 de 40 (pierde Nagios) |
  | `initial_prompt` | 3.90 % | +0.31 pts (−0.93 a +1.70) | 39 de 40 (pierde Plin) |
  | `hotwords` | 3.63 % | +0.42 pts (−0.83 a +1.71) | 40 de 40 |

- **Por qué `hotwords`.** Ningún mecanismo mejora el WER de forma significativa: los dos intervalos contienen el 0. La diferencia está en los términos del glosario:
  - `initial_prompt` escribe «Plim» en L4, y `metodo_pago` queda vacío en lugar de `plin`.
  - Sin glosario, Nagios sale «nacos» en E3. Nagios no es un valor de `tecnologias`: es la trampa de E3, una herramienta que el candidato dejó de usar. Con «nacos» la trampa desaparece y el acierto del campo no prueba la regla.
  - Con `hotwords`, Nagios llega bien transcrito y la extracción lo excluye igual. Además, es el único mecanismo que no pierde ningún término.
- **Riesgo.** Los clips que empeoran con un glosario no fallan en los términos: Whisper repite una frase entera. Con `hotwords`, L4 repite la dirección (WER 8.7 %); con `initial_prompt`, E1 repite una oración (6.5 %).

## Resultados Task 1

Corrida principal: la configuración por defecto del motor, `large-v3` en float16 con glosario `hotwords`, sobre la T4 de Colab y los 10 clips. Todo se calcula desde `data/cache/`, sin transcribir: `notebooks/06_resultados.ipynb`, secciones 1 a 3. Las otras 6 corridas aparecen ahí como comparación.

### Capa de transcripción

| WER | IC 95 % del WER por clip | CER | Velocidad | VRAM pico |
|---|---|---|---|---|
| 3.63 % | 2.71 % a 5.64 % | 2.57 % | 7.8 s por minuto de audio | 5558 MB (5002 MB de la corrida) |

### Capa de registro

Exactitud por campo con intervalo de Wilson al 95 %. El techo es la misma extracción sobre las referencias (el texto del guion), que acierta 60 de 60.

| Campo | Aciertos | IC 95 % | | Campo | Aciertos | IC 95 % |
|---|---|---|---|---|---|---|
| `anios_experiencia` | 5/5 | 0.57 a 1 | | `items` | 5/5 | 0.57 a 1 |
| `ultimo_puesto` | 3/5 | 0.23 a 0.88 | | `promocion` | 5/5 | 0.57 a 1 |
| `tecnologias` | 5/5 | 0.57 a 1 | | `descuento` | 5/5 | 0.57 a 1 |
| `pretension_salarial` | **1/5** | 0.04 a 0.62 | | `direccion_entrega` | **1/5** | 0.04 a 0.62 |
| `disponibilidad` | 5/5 | 0.57 a 1 | | `metodo_pago` | 5/5 | 0.57 a 1 |
| `nivel_ingles` | 5/5 | 0.57 a 1 | | `total_dicho` | 5/5 | 0.57 a 1 |

- **Total:** 50 de 60 campos, contra 60 de 60 del techo.
- **`nivel_ingles`:** macro F1 = 1.0.
- **Numéricos:** `anios_experiencia`, `total_dicho` y `descuento` tienen error absoluto 0. `pretension_salarial` no da valor en 3 de 5 clips y, donde da, el error medio es 250 soles (E3 sale 10000 en lugar de 9500).
- **Verificación:** 49 campos correctos quedan `verificado` y 1 `sin_verificar` (los 2.5 años de E4, que nunca se dicen). De los 10 errados, 6 quedan `no_mencionado` y **4 quedan `verificado`**: el valor equivocado aparece literal en la transcripción, y la verificación comprueba presencia, no corrección.
- **Por qué se pierden los 10 campos.** Casi ninguno es una palabra mal oída: son diferencias de formato entre cómo escribe Whisper y cómo están escritos los guiones.
  - **Separador de miles:** "6.500" y "$1.800" se leen como 6.5 y 1.8 y caen bajo el monto mínimo (pretensión de E1, E2 y E3).
  - **Guion:** "semi-senior" y "front-end" cortan el cargo (E1 y E4).
  - **Coma o punto junto al número:** "Calle Los Cedros, 245" no encaja en el patrón de dirección (L1, L2 y L5).
  - **Palabra mal oída:** "Girón" por "Jirón" en L3, el único fallo de oído.
  - **Lo que se dijo:** en E5 el salario actual y la pretensión quedaron en una sola oración.

  Las reglas no se corrigieron en esta evaluación.

### ¿Se puede saber si el registro sirve mirando solo el WER?

No. En la corrida principal:
- **E1 tiene el WER más bajo (1.08 %) y el peor registro (4 de 6).** "6.500" y "semi-senior" no cuentan como error en el WER, porque la normalización quita el separador y el guion, pero rompen dos campos.
- **L4 tiene el WER más alto (8.67 %) y el único registro perfecto (6 de 6).** Su WER viene de una frase entera que Whisper repite, y esa frase no toca ningún campo.
- **L4 con `initial_prompt`** tiene menos WER que con `hotwords` (7.14 % contra 8.67 %), pero un solo error, "Plim" por "Plin", deja vacío `metodo_pago`.

La correlación de Spearman entre el WER y los campos correctos es −0.29 sobre los 62 puntos, y dentro de `large-v3` cambia de signo (+0.33). **Quien reporte solo el WER puede elegir entre un modelo peor y uno mejor, pero no puede afirmar que el registro sea utilizable: eso se mide campo por campo.** El gráfico está en `data/resultados/wer_contra_registro.png`.

## Resultados Task 2

## Herramientas de IA y MCP

## Consentimiento y datos inventados

## Limitaciones

- E3 dura 1.97 min, 1.6 s por debajo del mínimo de 2 minutos (ver "Audios").
