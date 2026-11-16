# Blender para IA

Laboratorio de creación, transferencia e inspección de proyectos Blender mediante dos entornos Blender independientes.

## Arquitectura obligatoria

El sistema contiene dos entornos distintos. No se deben fusionar ni conectar entre sí:

1. **Entorno A — laboratorio experimental del agente (headless independiente).** Aquí se crean y modifican escenas, modelos, scripts y archivos `.blend`. No se conecta a GitHub Actions, al Bridge del repositorio ni a la instancia gráfica. Su salida es un archivo de proyecto y los recursos que lo acompañan.
2. **Entorno B — instancia real del repositorio (Blender GUI en GitHub Actions).** Actions descarga y ejecuta Blender con interfaz gráfica. El headless del repositorio es el controlador de esta instancia: le envía operaciones permitidas mediante AI Bridge y API `bpy`, y solicita evidencias visuales. No es el laboratorio experimental A.

**Flujo:** crear y probar en A → guardar el proyecto → transferirlo al repositorio → abrirlo en Blender GUI de Actions (B) → inspeccionar, ejecutar pruebas y capturar imágenes/vídeo → corregir en A y repetir.

La transferencia de archivos es explícita. A no abre sockets hacia B y B no controla A. El archivo `.blend` es la frontera entre ambos entornos.

## Blender persistente para el entorno A

El binario oficial **Blender 4.5.3 Linux x64** ya está publicado en una GitHub Release permanente, separado del historial de código:

- [Release Blender 4.5.3 — Runtime A](https://github.com/decuvilan-lgtm/Blender-para-ia/releases/tag/blender-4.5.3-linux-x64)
- Asset: `blender-4.5.3-linux-x64.tar.xz` (377.397.328 bytes).
- SHA-256 verificado: `975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845`.
- El workflow `.github/workflows/preserve-blender-runtime.yml` descarga el binario desde el distribuidor oficial, verifica su manifiesto SHA-256 y lo publica como Release asset.
- El bootstrap de A descarga desde GitHub, verifica de nuevo el SHA-256 y extrae la instalación en la caché local. Así A no depende del CDN oficial para obtener el binario.

## Estado actual

**B está validado visualmente**: Blender 4.5.3 abre en el escritorio virtual 1600×900, el Bridge local ejecuta operaciones `bpy`, y las capturas PNG/MP4 muestran la escena. [Evidencia de smoke test](https://github.com/decuvilan-lgtm/Blender-para-ia/actions/runs/43798586367/artifacts/14195532049).

**A ya tiene el binario preservado en GitHub y el bootstrap preparado para recuperarlo.** Falta ejecutar el bootstrap y comprobar Blender real dentro del runtime A, crear allí el proyecto de validación y completar el traspaso de ese archivo a B. La publicación del asset no se considera una prueba de ejecución en A.

## Blender GUI en GitHub Actions

1. Abre **Actions**.
2. Selecciona **Blender GUI Session**.
3. Pulsa **Run workflow**.
4. Selecciona una operación y ejecuta.
5. Descarga `blender-session-evidence` y revisa capturas, vídeo, proyecto y logs.

Si transferiste un `.blend` al repositorio, completa `project_path` con su ruta exacta. La sesión GUI B dura como máximo 10 minutos por ejecución; los proyectos deben guardarse y transferirse/restaurarse explícitamente.

## Componentes

- `ai_lab/experimental/`: bootstrap y launcher del entorno A.
- `session_system/blender_bridge/`: Bridge Python dentro de Blender GUI B.
- `session_system/repo_headless/`: controlador headless del repositorio para B.
- `session_system/scripts/`: captura y validación de evidencias.
- `.github/workflows/`: ciclo de vida de B y preservación del binario A.

## Seguridad y límites

- El Bridge escucha en `127.0.0.1` dentro del runner; no equivale a un canal remoto desde el agente/chat.
- No se acepta código Python arbitrario por TCP; solo operaciones explícitamente permitidas.
- El entorno A no utiliza el Bridge ni el cliente B.
- El binario de Blender se conserva como Release asset, no dentro del historial Git.
- Blender se distribuye bajo sus licencias aplicables; el proyecto conserva la procedencia oficial y el checksum del binario.


### Instalar Blender en el entorno A del asistente

La descarga directa del CDN oficial puede no estar disponible desde el runtime experimental. El procedimiento alternativo ya está preparado y el puente de transferencia fue probado: Actions descarga la Release permanente, verifica el SHA-256 y divide el archivo en cinco artefactos pequeños; el conector de GitHub los descarga y se materializan en el espacio de trabajo de A.

**Guía visible y pasos exactos:** [docs/environment-a-install.md](docs/environment-a-install.md).

Estado: los cinco fragmentos ya se transfirieron al almacenamiento de trabajo de A. La unión, extracción y ejecución de Blender aún están pendientes de una sesión de shell funcional; no se declara instalado hasta que `blender --version` y la prueba `A_RUNTIME_OK 4.5.3` pasen dentro de A.
