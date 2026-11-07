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
- **Formato de Whisper** (versión 2; casos en la sección 1.5 del notebook 03). Corrige cómo escribe Whisper, no lo que oye, y lo ven igual la extracción, la verificación y el WER:
  - **Separador de miles**: un punto o una coma seguidos de exactamente tres dígitos son de miles ("6.500" → 6500); "4.5" sigue siendo decimal. Caso ambiguo: un decimal de tres cifras ("2.125 kilos") se lee como 2125. En el corpus no hay ninguno.
  - **Símbolos de moneda**: "$1.800" → "1800 dólares", "S/ 6500" → "6500 soles". `$` es dólar porque el corpus es de Lima: el sol se escribe `S/` y `$` se usa para el dólar. En México o Chile sería el peso.
  - **Guion entre letras**: "semi-senior" → "semi senior", la forma del ground truth. "front-end" queda "front end", que no es "frontend".
  - **Direcciones**: se acepta una coma o un punto entre el nombre de la vía y el número ("Calle Los Cedros, 245").
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
  | sin glosario | 3.52 % | — | 39 de 40 (pierde Nagios) |
  | `initial_prompt` | 3.87 % | +0.31 pts (−0.93 a +1.70) | 39 de 40 (pierde Plin) |
  | `hotwords` | 3.59 % | +0.42 pts (−0.83 a +1.71) | 40 de 40 |

- **Por qué `hotwords`.** Ningún mecanismo mejora el WER de forma significativa: los dos intervalos contienen el 0. La diferencia está en los términos del glosario:
  - `initial_prompt` escribe «Plim» en L4, y `metodo_pago` queda vacío en lugar de `plin`.
  - Sin glosario, Nagios sale «nacos» en E3. Nagios no es un valor de `tecnologias`: es la trampa de E3, una herramienta que el candidato dejó de usar. Con «nacos» la trampa desaparece y el acierto del campo no prueba la regla.
  - Con `hotwords`, Nagios llega bien transcrito y la extracción lo excluye igual. Además, es el único mecanismo que no pierde ningún término.
- **Riesgo.** Los clips que empeoran con un glosario no fallan en los términos: Whisper repite una frase entera. Con `hotwords`, L4 repite la dirección (WER 8.7 %); con `initial_prompt`, E1 repite una oración (6.5 %).

## Resultados Task 1

Corrida principal: la configuración por defecto del motor, `large-v3` en float16 con glosario `hotwords`, sobre la T4 de Colab y los 10 clips. Todo se calcula desde `data/cache/`, sin transcribir: `notebooks/06_resultados.ipynb`, secciones 1 a 5. Las otras 6 corridas aparecen ahí como comparación.

### Capa de transcripción

| WER | IC 95 % del WER por clip | CER | Velocidad | VRAM pico |
|---|---|---|---|---|
| 3.59 % | 2.63 % a 5.64 % | 2.52 % | 7.8 s por minuto de audio | 5558 MB (5002 MB de la corrida) |

### Capa de registro

Exactitud por campo con intervalo de Wilson al 95 %, con la versión 2 de las reglas. El techo es la misma extracción sobre las referencias (el texto del guion), que acierta 60 de 60.

| Campo | Aciertos | IC 95 % | | Campo | Aciertos | IC 95 % |
|---|---|---|---|---|---|---|
| `anios_experiencia` | 5/5 | 0.57 a 1 | | `items` | 5/5 | 0.57 a 1 |
| `ultimo_puesto` | 4/5 | 0.38 a 0.96 | | `promocion` | 5/5 | 0.57 a 1 |
| `tecnologias` | 5/5 | 0.57 a 1 | | `descuento` | 5/5 | 0.57 a 1 |
| `pretension_salarial` | 4/5 | 0.38 a 0.96 | | `direccion_entrega` | **3/5** | 0.23 a 0.88 |
| `disponibilidad` | 5/5 | 0.57 a 1 | | `metodo_pago` | 5/5 | 0.57 a 1 |
| `nivel_ingles` | 5/5 | 0.57 a 1 | | `total_dicho` | 5/5 | 0.57 a 1 |

- **Total:** 56 de 60 campos (IC 95 %: 0.84 a 0.97), contra 60 de 60 del techo.
- **Versión 1.** La primera evaluación con audio real (PR #7) daba 50 de 60. Casi todos sus fallos venían de cómo escribe Whisper ("6.500", "$1.800", "semi-senior", "Calle Los Cedros, 245"), y de ahí salió la corrección de formato. La versión 1 sigue en las secciones 2 a 4 del notebook 06, y sus tablas, en `data/resultados/*_v1.csv`.
- **`nivel_ingles`:** macro F1 = 1.0.
- **Numéricos:** `anios_experiencia`, `total_dicho` y `descuento` tienen error absoluto 0. `pretension_salarial` también, salvo E5, que no da valor.
- **Verificación:** 55 campos correctos quedan `verificado` y 1 `sin_verificar` (los 2.5 años de E4, que nunca se dicen). De los 4 errados, 2 quedan `no_mencionado` y **2 quedan `verificado`**: la verificación comprueba presencia, no corrección.
- **Por qué fallan los 4 que quedan.**
  - **E4, `ultimo_puesto`:** Whisper escribe "front-end" y el ground truth, "frontend". El guion equivale al espacio, no a la palabra unida.
  - **E5, `pretension_salarial`:** el salario actual y la pretensión se dijeron en una sola oración, y la regla descarta la oración entera.
  - **L3, `direccion_entrega`:** "Girón" por "Jirón". Es un error de oído y no se corrige.
  - **L5, `direccion_entrega`:** Whisper pone un punto después del número ("2271. Bloque C."), los complementos quedan en otra oración, y además oye "San Juan del Urigancho".

### ¿Se puede saber si el registro sirve mirando solo el WER?

No clip por clip, aunque con la versión 2 se acercan más. Los casos se buscan con criterios explícitos (`notebooks/06_resultados.ipynb`, secciones 3.1, 5.6 y 5.6.1):

- **WER alto y registro perfecto:** WER en el cuartil superior de los 62 puntos y 6 de 6 campos.
- **WER bajo y registro roto:** WER por debajo de la mediana de su corrida y al menos un campo errado. Primero van los que pierden un campo crítico (`pretension_salarial`, `anios_experiencia` o `total_dicho`).

En la corrida principal:
- **L4 tiene el WER más alto (8.67 %) y el registro perfecto (6 de 6).** Su WER viene de una frase entera que Whisper repite, y esa frase no toca ningún campo.
- **L4 con `initial_prompt`** tiene menos WER que con `hotwords` (7.14 % contra 8.67 %), pero un solo error, "Plim" por "Plin", deja vacío `metodo_pago`.
- **E5 es el caso de WER bajo y registro roto de la versión 2.** Su WER es 2.50 %, debajo de la mediana de la corrida (3.41 %), y pierde `pretension_salarial`, el dato crítico. El guion dice "Hoy gano seis mil doscientos. Mi pretensión es de siete mil", en dos oraciones. La transcripción dice "Actualmente gano 6200, pero mi pretensión es de 7000", en una. La regla descarta la oración del salario actual, y con ella la pretensión. El WER cuenta esa diferencia como 2 errores entre unas 280 palabras, y el punto perdido no lo cuenta. Es el único clip de la corrida que cumple. E4 pierde `ultimo_puesto`, pero su WER (5.86 %) está por encima de la mediana.
- **E1 era el caso de la versión 1, y explica por qué la normalización del WER esconde errores de formato.** Tiene el WER más bajo (1.08 %) y daba 4 de 6: "6.500" y "semi-senior" no cuentan como error en el WER, porque la normalización quita el separador y el guion, pero rompían dos campos. Con la versión 2 de las reglas, E1 da 6 de 6.

La correlación de Spearman entre el WER y los campos correctos pasa de −0.29 a −0.54 sobre los 62 puntos y, dentro de `large-v3`, de +0.33 a −0.31. **El WER sirve para elegir entre un modelo peor y uno mejor, pero no para afirmar que el registro de un clip es utilizable: eso se mide campo por campo.** El gráfico está en `data/resultados/wer_contra_registro.png`, y el de la versión 1, en `wer_contra_registro_v1.png`.

## Resultados Task 2

## Herramientas de IA y MCP

## Consentimiento y datos inventados

## Limitaciones

- La normalización asume que `$` es dólar y que un punto seguido de tres dígitos es de miles. Las dos reglas valen para este corpus de Lima, pero no en general (ver "Normalización de números").
- E3 dura 1.97 min, 1.6 s por debajo del mínimo de 2 minutos (ver "Audios").
