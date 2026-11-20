# Experimental Blender Lab — Entorno A

Este paquete es el laboratorio experimental independiente del agente. No es el controlador del Blender de GitHub Actions.

## Responsabilidad

- Ejecutar Blender con `--background`.
- Crear y modificar escenas, objetos, materiales, scripts y proyectos `.blend`.
- Ejecutar pruebas headless y renderizar.
- Guardar resultados para transferirlos al repositorio y que B los abra e inspeccione.

## Aislamiento obligatorio

Este entorno **no** se conecta al AI Bridge, no usa `session_system/repo_headless/client.py`, no consulta ni controla la instancia gráfica de Actions y no necesita una sesión activa de Actions. Su resultado se transfiere como archivo.

El headless del repositorio (Entorno B) tiene una función distinta: controlar la instancia Blender GUI B que corre en Actions. No ejecutar ese cliente desde este laboratorio A.

## Blender persistente

El binario oficial Blender 4.5.3 Linux x64 está conservado como asset de GitHub Release, fuera del historial Git:

- Release: https://github.com/decuvilan-lgtm/Blender-para-ia/releases/tag/blender-4.5.3-linux-x64
- Archivo: `blender-4.5.3-linux-x64.tar.xz`
- SHA-256: `975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845`

El bootstrap descarga el asset desde GitHub, verifica el SHA-256 y lo extrae en `~/.cache/blender-for-ai`.

## Preparar y comprobar Blender

En Linux con `curl`, `sha256sum` y `tar`:

```bash
chmod +x bootstrap.sh run_headless.sh
./run_headless.sh --python-expr "import bpy; print('Blender:', bpy.app.version_string)"
```

## Instalar desde los artefactos ya transferidos

Si el CDN o la descarga directa no están disponibles, Actions puede transportar la Release en cinco ZIP pequeños. Descarga los cinco fragmentos y el ZIP de checksums, materialízalos juntos en una carpeta y ejecuta:

```bash
bash ai_lab/experimental/assemble_transferred_runtime.sh /path/to/transfer-directory
```

El script verifica los hashes individuales y el SHA-256 del archivo completo antes de extraer. Luego comprueba Blender en modo headless y debe imprimir `A_RUNTIME_OK 4.5.3`.

La guía detallada está en [docs/environment-a-install.md](../../docs/environment-a-install.md).

## Crear una escena de validación en A

Una vez instalado y probado el runtime:

```bash
./run_headless.sh --python "$PWD/scripts/create_validation_scene.py" -- "$PWD/output/validation-scene.blend"
./run_headless.sh "$PWD/output/validation-scene.blend" --python "$PWD/scripts/validate_project.py"
```

El script de creación genera una escena con suelo, cubo, esfera, toroide, rótulo, cámara y luces, guarda el proyecto `.blend` y renderiza una imagen PNG.

## Usar Actions como ojos visuales de Blender (Entorno B)

El workflow `.github/workflows/blender-session.yml` mantiene una instancia gráfica real de Blender 4.5.3 dentro de GitHub Actions (Xvfb + Openbox) y permite controlarla mediante el puente local autenticado.

### Prueba visual automatizada

En Actions → **Blender GUI Session**, seleccionar `visual-test`. También se inicia automáticamente al modificar el workflow o los archivos del puente. La operación:

1. Crea una escena de prueba con cubo, cámara y luz.
2. Guarda `visual-test.blend`.
3. Renderiza `preview.png` con Eevee Next; si el motor devuelve una excepción, intenta Workbench.
4. Devuelve metadatos de la escena (objetos, cámara, motor, resolución y versión).
5. Captura el escritorio X11 como `desktop.png` y graba un vídeo breve de la sesión.
6. Publica el proyecto, el render, las capturas, el vídeo y los logs en el artefacto `blender-session-evidence`.

El CLI también admite `visual-test` directamente. Los artefactos se descargan desde el resumen de la ejecución de Actions y se pueden inspeccionar aquí para validar visualmente el resultado. El PNG renderizado es la evidencia principal del contenido; `desktop.png` demuestra qué estaba mostrando la interfaz gráfica.

**Primera ejecución de esta ruta:** [run 44644302051](https://github.com/decuvilan-lgtm/Blender-para-ia/actions/runs/44644302051). Su resultado debe comprobarse antes de considerar validada la ruta completa.

## Transferir a B

1. Comprueba que el `.blend` y su PNG existan y tengan tamaño no nulo.
2. Sube/versiona el proyecto bajo `projects/inbox/` en el repositorio.
3. Abre **Actions → Blender GUI Session → Run workflow**.
4. En `project_path`, indica la ruta exacta del `.blend`.
5. Actions abre el archivo en su propia instancia Blender GUI B.

## Estado verificado

- B ya cuenta con pruebas GUI satisfactorias en Actions.
- La Release permanente y los seis ZIP de transferencia del run [43805163265](https://github.com/decuvilan-lgtm/Blender-para-ia/actions/runs/43805163265) están publicados.
- Los seis ZIP de ese run se materializaron en A en `/mnt/data/blender-transfer-run438051/`.
- **Aún no se ha verificado** la unión, extracción ni ejecución real de Blender en A: la herramienta de shell/Python del runtime devuelve un error de infraestructura. No confundir la transferencia de archivos ni el entorno B con una instalación funcional de A.
