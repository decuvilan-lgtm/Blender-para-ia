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

### Binario persistente

Blender 4.5.3 Linux x64 está almacenado como asset de GitHub Release, no como blob de Git:

- Release: https://github.com/decuvilan-lgtm/Blender-para-ia/releases/tag/blender-4.5.3-linux-x64
- Asset: `blender-4.5.3-linux-x64.tar.xz` (377.397.328 bytes).
- SHA-256: `975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845`.
- Workflow de publicación: `.github/workflows/preserve-blender-runtime.yml`.
- `ai_lab/experimental/bootstrap.sh` descarga el asset desde GitHub, verifica el SHA-256 y lo extrae en la caché local.

La existencia del asset confirma su preservación, no que Blender ya se haya ejecutado dentro del runtime A. Esa prueba sigue pendiente.

## Transferencia A → repositorio

1. A termina una modificación y guarda el proyecto.
2. Se comprueba que el archivo existe, tiene extensión `.blend` y tamaño no nulo.
3. Se transfiere al repositorio (destino recomendado: `projects/inbox/`).
4. Se registra el commit o identificador del archivo transferido.
5. Actions recibe la ruta exacta del proyecto como entrada y lo abre en Blender GUI B.
6. Se conservan el proyecto de entrada, el proyecto resultante y los logs como evidencia.

No se debe copiar el ejecutable completo de Blender al historial Git. El runtime está preservado en Releases; los proyectos se versionan explícitamente.

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
| Blender A binario preservado en GitHub Release | Verificado: asset de 377.397.328 bytes y SHA-256 registrado |
| A: bootstrap desde GitHub + verificación checksum | Implementado; ejecución en runtime A pendiente |
| A: launcher headless independiente | Scripts y generador/validador escritos; ejecución Blender A pendiente |
| A → repositorio: transferencia automática de proyectos | Pendiente; B acepta ruta de un .blend versionado mediante project_path |
| B: Blender GUI en Actions | Verificado visualmente en smoke test: ventana maximizada a 1600×900 |
| Headless B → Blender GUI B por Bridge local | Verificado: ping, scene-info y create-demo ejecutados en la instancia gráfica |
| Órdenes remotas desde el agente durante una sesión | Pendiente |
| Capturas y vídeo verificados | Verificados: PNG y fotograma MP4 1600×900, 5 s H.264; inspección visual correcta |

Este documento es el contrato técnico de referencia. Si un workflow, script o README contradice estas reglas, debe corregirse el código/documento; no se debe reinterpretar la arquitectura para justificarlo.
