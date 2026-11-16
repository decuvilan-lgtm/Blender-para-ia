# Blender para IA

Laboratorio de creación, transferencia e inspección de proyectos Blender mediante dos entornos Blender independientes.

## Arquitectura obligatoria

El sistema contiene dos entornos distintos. No se deben fusionar ni conectar entre sí:

1. **Entorno A — laboratorio experimental del agente (headless independiente).** Aquí se crean y modifican escenas, modelos, scripts y archivos `.blend`. No se conecta a GitHub Actions, al Bridge del repositorio ni a la instancia gráfica. Su salida es un archivo de proyecto y los recursos que lo acompañan.
2. **Entorno B — instancia real del repositorio (Blender GUI en GitHub Actions).** Actions descarga y ejecuta Blender con interfaz gráfica. El headless del repositorio es el controlador de esta instancia: le envía operaciones permitidas mediante AI Bridge y API `bpy`, y solicita evidencias visuales. No es el laboratorio experimental A.

**Flujo:** crear y probar en A → guardar el proyecto → transferirlo al repositorio → abrirlo en Blender GUI de Actions (B) → inspeccionar, ejecutar pruebas y capturar imágenes/vídeo → corregir en A y repetir.

La transferencia de archivos es explícita. A no abre sockets hacia B y B no controla A. El archivo `.blend` es la frontera entre ambos entornos.

Consulta [docs/architecture.md](docs/architecture.md) para las responsabilidades, el ciclo de transferencia, las reglas de aislamiento y el estado de las conexiones.

## Estado actual

**Infraestructura en construcción.** La separación A/B está definida, pero el canal remoto interactivo y la transferencia automatizada todavía no están terminados. La primera captura fue negra por una configuración incorrecta de geometría de ventana. Tras corregirla, el smoke test `43798100974` terminó correctamente y se inspeccionaron el PNG y el primer fotograma del MP4: muestran Blender 4.5.3 ocupando el escritorio 1600×900. Esto valida la GUI de B y el flujo de evidencias; la ejecución real del laboratorio A y la transferencia de un proyecto creado allí siguen pendientes.

No se considera superada una prueba visual si la imagen o el vídeo están vacíos, negros o no muestran la instancia Blender. El workflow debe fallar ante una captura PNG negra.

## Blender GUI en GitHub Actions

1. Abre la pestaña **Actions**.
2. Selecciona **Blender GUI Session**.
3. Pulsa **Run workflow**.
4. Selecciona una operación y ejecuta.
5. Descarga `blender-session-evidence` y revisa las capturas, el vídeo, el proyecto y los logs.

El runner hospedado es efímero. La sesión está limitada a un máximo configurable de 10 minutos; al finalizar, otra ejecución inicia una nueva instancia. Los proyectos deben guardarse y transferirse/restaurarse explícitamente.

## Componentes

- `ai_lab/experimental/`: bootstrap y launcher del entorno A; descarga Blender al prepararse y lo ejecuta en background, sin conexión con Actions.
- `session_system/blender_bridge/`: Bridge Python cargado dentro de Blender GUI en B. Las llamadas `bpy` se ejecutan en el hilo principal.
- `session_system/repo_headless/`: controlador headless del repositorio para la instancia B.
- `session_system/scripts/`: captura y validación de evidencias.
- `.github/workflows/`: ciclo de vida de la instancia gráfica B.

## Seguridad y límites

- El Bridge escucha en `127.0.0.1` dentro del runner; esto solo permite conexiones desde procesos del mismo runner. **No equivale a un canal remoto desde el agente/chat.**
- No se acepta código Python arbitrario por TCP; solo operaciones explícitamente permitidas.
- El token se pasa mediante variable de entorno y no se guarda en el repositorio.
- El controlador B y Blender GUI B comparten runner en la implementación actual. El control remoto desde fuera del runner sigue pendiente; no se debe afirmar que ya existe.
- El entorno A no utiliza ese Bridge ni el cliente B.
- El paquete experimental contiene scripts y descarga el binario oficial al prepararse; no se sube el ejecutable de Blender (más de 1 GB) al repositorio.

## Versión y licencias

La infraestructura fija Blender 4.5.3 para reproducibilidad. Esta fase no copia el código fuente completo de Blender al repositorio. Antes de redistribuir binarios o partes del proyecto se revisarán las licencias y obligaciones aplicables.
