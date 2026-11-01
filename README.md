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

## Resultados Task 1

## Resultados Task 2

## Herramientas de IA y MCP

## Consentimiento y datos inventados

## Limitaciones
