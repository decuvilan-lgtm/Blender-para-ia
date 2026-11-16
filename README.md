# Blender para IA

Laboratorio de creación, transferencia e inspección de proyectos Blender mediante dos entornos Blender independientes.

## Arquitectura obligatoria

El sistema contiene dos entornos distintos. No se deben fusionar ni conectar entre sí:

1. **Entorno A — laboratorio experimental del agente (headless independiente).** Aquí se crean y modifican escenas, modelos, scripts y archivos `.blend`. No se conecta a GitHub Actions, al Bridge del repositorio ni a la instancia gráfica. Su salida es un archivo de proyecto y los recursos que lo acompañan.
2. **Entorno B — instancia real del repositorio (Blender GUI en GitHub Actions).** Actions descarga y ejecuta Blender con interfaz gráfica. El headless del repositorio es el controlador de esta instancia: le envía operaciones permitidas mediante AI Bridge y API `bpy`, y solicita evidencias visuales. No es el laboratorio experimental A.

**Flujo:** crear y probar en A → guardar el proyecto → transferirlo al repositorio → abrirlo en Blender GUI de Actions (B) → inspeccionar, ejecutar pruebas y capturar imágenes/vídeo → corregir en A y repetir.

La transferencia de archivos es explícita. A no abre sockets hacia B y B no controla A. El archivo `.blend` es la frontera entre ambos entornos.

## Blender persistente para el entorno A

El binario oficial **Blender 4.5.3 Linux x64** está publicado en una GitHub Release permanente, separado del historial de código:

- [Release Blender 4.5.3 — Runtime A](https://github.com/decuvilan-lgtm/Blender-para-ia/releases/tag/blender-4.5.3-linux-x64)
- Asset: `blender-4.5.3-linux-x64.tar.xz` (377.397.328 bytes).
- SHA-256: `975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845`.
- El workflow de preservación publica el asset; el bootstrap de A lo descarga desde GitHub y verifica su hash antes de extraerlo.

## Estado actual

**B está validado visualmente**: Blender 4.5.3 abre en el escritorio virtual 1600×900, el Bridge local ejecuta operaciones `bpy`, y las capturas PNG/MP4 muestran la escena. [Evidencia de smoke test](https://github.com/decuvilan-lgtm/Blender-para-ia/actions/runs/43798586367/artifacts/14195532049).

**A tiene el runtime preservado y los artefactos de transferencia materializados**, pero la ejecución real de Blender dentro de A sigue pendiente. El workflow de transferencia [43805163265](https://github.com/decuvilan-lgtm/Blender-para-ia/actions/runs/43805163265) terminó correctamente y sus cinco partes más el manifiesto están en `/mnt/data/blender-transfer-run438051/`. La herramienta de shell/Python de A está devolviendo un error de infraestructura; por eso no se afirma que Blender ya esté instalado ni ejecutándose en A.

La guía exacta y el procedimiento para continuar están en [docs/environment-a-install.md](docs/environment-a-install.md). El ensamblador/instalador verificador está en [ai_lab/experimental/assemble_transferred_runtime.sh](ai_lab/experimental/assemble_transferred_runtime.sh).

## Blender GUI en GitHub Actions (B)

1. Abre **Actions**.
2. Selecciona **Blender GUI Session**.
3. Pulsa **Run workflow**.
4. Selecciona una operación y ejecuta.
5. Descarga `blender-session-evidence` y revisa capturas, vídeo, proyecto y logs.

Si transferiste un `.blend`, completa `project_path` con su ruta exacta. La sesión GUI B dura como máximo 10 minutos por ejecución; los proyectos deben guardarse y transferirse/restaurarse explícitamente.

## Componentes

- `ai_lab/experimental/`: bootstrap, launcher y ensamblador/instalador de A.
- `session_system/blender_bridge/`: Bridge Python dentro de Blender GUI B.
- `session_system/repo_headless/`: controlador headless del repositorio para B.
- `session_system/scripts/`: captura y validación de evidencias.
- `.github/workflows/`: ciclo de vida de B y preservación/transferencia del binario A.

## Seguridad y límites

- El Bridge escucha en `127.0.0.1` dentro del runner; no equivale a un canal remoto desde el agente/chat.
- No se acepta código Python arbitrario por TCP; solo operaciones explícitamente permitidas.
- El entorno A no utiliza el Bridge ni el cliente B.
- El binario de Blender se conserva como Release asset, no dentro del historial Git.
- Blender se distribuye bajo sus licencias aplicables; el proyecto conserva la procedencia oficial y el checksum del binario.
