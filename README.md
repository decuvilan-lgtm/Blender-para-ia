# Blender para IA

Laboratorio para experimentar, ejecutar y verificar Blender desde GitHub Actions sin importar el código fuente completo de Blender al repositorio.

## Objetivo inicial

- Abrir Blender con interfaz gráfica dentro de un runner de GitHub Actions.
- Mantener una sesión automatizada de hasta 10 minutos.
- Controlar la instancia mediante un complemento Python (AI Bridge) y la API `bpy`, no mediante clics por coordenadas.
- Enviar órdenes desde el cliente headless del repositorio por `localhost`.
- Generar capturas, vídeos, logs y proyectos como artefactos de Actions.
- Empaquetar el laboratorio experimental como artefacto descargable.

## Estado

**Fase 1 — infraestructura mínima en construcción.** Este repositorio no contiene todavía el código fuente de Blender. Blender se descarga durante el workflow; así evitamos subir gigabytes al repositorio y ralentizar cada cambio.

## Primera prueba

1. Abre la pestaña **Actions**.
2. Selecciona **Blender GUI Session**.
3. Pulsa **Run workflow**.
4. Elige una operación (por defecto `create-demo`) y ejecuta.
5. Descarga el artefacto `blender-session-evidence`.

El workflow usa un runner Ubuntu hospedado por GitHub, un display virtual Xvfb y una instancia gráfica de Blender. La ventana se mide desde el arranque de Blender y tiene un máximo de 10 minutos. Esta primera versión recibe una operación al iniciar la ejecución; todavía no ofrece una consola de órdenes en vivo desde otra ejecución o desde el chat. Para otra operación se abre una nueva sesión.

## Arquitectura

- `session_system/blender_bridge/`: complemento/servidor TCP que vive dentro de Blender y ejecuta operaciones permitidas en el hilo principal de Blender.
- `session_system/repo_headless/`: cliente headless que envía órdenes al Bridge.
- `session_system/scripts/`: capturas y utilidades.
- `ai_lab/experimental/`: laboratorio reproducible que se empaqueta como artefacto.
- `.github/workflows/`: automatización de sesiones.

## Seguridad y límites de esta primera versión

- El Bridge escucha únicamente en `127.0.0.1`.
- No acepta código Python arbitrario por la red; solo operaciones explícitamente implementadas.
- El token se pasa mediante variable de entorno y nunca se guarda en el repositorio.
- Los runners hospedados de GitHub son efímeros. Una sesión no queda viva entre ejecuciones: al reabrirla se inicia otro Blender. La escena se guarda automáticamente como artefacto para poder restaurarla en una fase posterior. El paquete experimental contiene scripts y bootstrap; descarga Blender al prepararse y no incluye el binario de más de 1 GB.
- Un workflow_dispatch abre una sesión y ejecuta la orden seleccionada en esa misma ejecución. El cliente y Blender comparten runner y `localhost`; otra ejecución independiente no puede conectarse al localhost de un runner anterior.

## Versiones

La primera prueba fija Blender 4.5.3 para que los resultados sean reproducibles. La versión podrá actualizarse tras validar compatibilidad.

## Licencias

Esta fase no copia ni redistribuye el código fuente de Blender. Antes de incorporar o distribuir partes del proyecto original, se documentarán las licencias y obligaciones aplicables a cada componente.
