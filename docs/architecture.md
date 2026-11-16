# Arquitectura y contrato de aislamiento

## Regla principal

Hay dos entornos Blender independientes y un archivo de proyecto como frontera de transferencia. No se permite que el entorno experimental del agente se conecte al Blender de Actions ni al Bridge del repositorio.

## Entorno A — laboratorio experimental del agente

**Propósito:** crear y experimentar.

- Ejecuta Blender en modo headless/background.
- Crea escenas, objetos, materiales, cámaras, luces, animaciones y scripts.
- Ejecuta validaciones y renders locales cuando el runtime lo permite.
- Guarda el resultado en un archivo `.blend` y sus recursos externos.
- No usa `session_system/repo_headless/client.py`.
- No abre conexión TCP con el Bridge de Actions.
- No depende de que una sesión de Actions esté activa.

El launcher `ai_lab/experimental/run_headless.sh` prepara Blender fijado y lo ejecuta con `--background`. El paquete no contiene el binario; lo obtiene del distribuidor oficial en el primer arranque.

## Transferencia A → repositorio

La transferencia debe ser explícita, verificable y reproducible:

1. A termina una modificación y guarda el proyecto.
2. Se comprueba que el archivo existe, tiene extensión `.blend` y tamaño no nulo.
3. Se transfiere al repositorio (destino recomendado: `projects/inbox/`).
4. Se registra el commit o identificador del archivo transferido.
5. Actions recibe la ruta exacta del proyecto como entrada y lo abre en Blender GUI B.
6. Se conservan el proyecto de entrada, el proyecto resultante y los logs como evidencia.

No se debe copiar el ejecutable completo de Blender al repositorio. Los proyectos pueden ser binarios, pero deben mantenerse pequeños y no se deben sobrescribir sin revisar su versión.

## Entorno B — Blender real de GitHub Actions

**Propósito:** inspeccionar y validar visualmente.

- Actions descarga Blender GUI en el runner.
- Blender se inicia bajo un display virtual X11.
- El Bridge se carga dentro del proceso Blender.
- El controlador headless del repositorio envía comandos al Bridge.
- El Bridge acepta solo operaciones allowlisted y ejecuta llamadas `bpy` mediante `bpy.app.timers` en el hilo principal.
- Se solicitan capturas y vídeos de la instancia real, además de información estructurada de la escena.
- Al terminar la sesión se guardan el proyecto y las evidencias como artifacts.

El headless B sí se conecta al Blender GUI B. En la implementación actual ambos procesos comparten el runner y el Bridge usa `127.0.0.1`. El agente externo todavía no tiene un canal de órdenes en vivo hacia el runner. No confundir el localhost del runner con acceso remoto.

## Ciclo iterativo

```text
Entorno A (crear y probar)
        |
        | archivo .blend + recursos
        v
Repositorio (transferencia versionada)
        |
        v
GitHub Actions: Blender GUI B
        ^
        | órdenes bpy mediante Bridge
        |
Headless B (controlador del repositorio)
        |
        v
Capturas + vídeo + logs + .blend de salida
        |
        v
Inspección → correcciones en A → nueva transferencia
```

## Reglas de aceptación

- Un `.blend` guardado no demuestra que la GUI sea visible.
- Un job en estado `success` no demuestra que la captura sea correcta.
- La captura debe tener píxeles válidos y mostrar evidencia de la sesión; una imagen negra debe hacer fallar la validación.
- Revisar el PNG y al menos un fotograma del MP4, no solo comprobar que los archivos existen.
- Si la ventana gráfica no aparece, conservar diagnóstico de Xvfb, OpenGL/Mesa, árbol de ventanas y logs.
- Nunca afirmar que A inspeccionó directamente B: A produce archivos; B los abre e inspecciona.

## Estado de implementación

| Capacidad | Estado |
|---|---|
| A: launcher headless independiente | Scripts implementados; falta validar ejecución en el entorno destino |
| A → repositorio: transferencia automática de proyectos | Pendiente |
| B: Blender GUI en Actions | Arranca, pero la captura visual inicial fue negra |
| Headless B → Blender GUI B por Bridge local | Prueba inicial parcial |
| Órdenes remotas desde el agente durante una sesión | Pendiente |
| Capturas y vídeo verificados | Pendiente; la primera captura no pasó |
| Restauración de proyectos transferidos | Pendiente de completar y probar |

Este documento es el contrato técnico de referencia. Si un workflow, script o README contradice estas reglas, debe corregirse el código/documento; no se debe reinterpretar la arquitectura para justificarlo.
