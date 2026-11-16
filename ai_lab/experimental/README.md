# Experimental Blender Lab — Entorno A

Este paquete es el laboratorio experimental independiente del agente. No es el controlador del Blender de GitHub Actions.

## Responsabilidad

- Ejecutar Blender con `--background`.
- Crear/modificar escenas, objetos, materiales, scripts y proyectos `.blend`.
- Ejecutar pruebas headless y renderizar.
- Guardar resultados para transferirlos al repositorio y que B los abra e inspeccione.

## Aislamiento obligatorio

Este entorno **no** se conecta al AI Bridge, no usa `session_system/repo_headless/client.py`, no consulta ni controla la instancia gráfica de Actions y no necesita una sesión activa de Actions. Su resultado se transfiere como archivo.

El headless del repositorio (Entorno B) tiene una función distinta: controlar la instancia Blender GUI B que corre en Actions. No ejecutar ese cliente desde este laboratorio A.

## Blender persistente en GitHub

El binario oficial Blender 4.5.3 Linux x64 está conservado como asset de GitHub Release, fuera del historial Git:

- Release: https://github.com/decuvilan-lgtm/Blender-para-ia/releases/tag/blender-4.5.3-linux-x64
- Archivo: `blender-4.5.3-linux-x64.tar.xz`
- SHA-256: `975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845`

El bootstrap de A descarga ese asset desde GitHub, verifica el SHA-256 y lo extrae en `~/.cache/blender-for-ai`. No depende del CDN de Blender durante la preparación normal.

## Preparar y comprobar Blender

En Linux con `curl`, `sha256sum` y `tar`:

```bash
chmod +x bootstrap.sh run_headless.sh
./run_headless.sh --python-expr "import bpy; print('Blender:', bpy.app.version_string)"
```

El primer inicio descarga y extrae el paquete; las siguientes ejecuciones reutilizan la instalación.

## Generar una escena de validación en A

```bash
./run_headless.sh --python "$PWD/scripts/create_validation_scene.py" -- "$PWD/output/validation-scene.blend"
```

El script crea una escena con suelo, cubo, esfera, toroide, rótulo, cámara y luces. Guarda el proyecto `.blend` y renderiza una imagen PNG junto a él.

Valida el archivo desde A:

```bash
./run_headless.sh "$PWD/output/validation-scene.blend" --python "$PWD/scripts/validate_project.py"
```

## Transferir a B

1. Comprueba que el `.blend` y su PNG existan y tengan tamaño no nulo.
2. Sube/versiona el proyecto bajo `projects/inbox/` en el repositorio.
3. Abre **Actions → Blender GUI Session → Run workflow**.
4. En `project_path`, indica la ruta exacta del `.blend`.
5. Actions abre el archivo en su propia instancia Blender GUI B.

## Estado

El binario A ya está preservado en GitHub y el bootstrap se ha configurado para descargarlo desde allí. La ejecución real de Blender en el runtime experimental A todavía debe verificarse; no se debe confundir la existencia del binario en GitHub con una ejecución ya realizada en A.


## Instalación desde el artefacto de GitHub

Si el runtime A no puede resolver el CDN de Blender, utiliza el puente de artefactos de Actions descrito en la guía principal: [docs/environment-a-install.md](../../docs/environment-a-install.md). El archivo permanente sigue siendo la Release asset; los artefactos divididos son un transporte temporal para superar el límite de materialización de 100 MiB por archivo.

**Estado de esta sesión:** los cinco ZIP de partes se descargaron desde Actions y se materializaron en `/mnt/data/blender-transfer-parts/`. La unión, extracción y ejecución aún no se han podido comprobar porque el servicio de shell del runtime devolvió un error de infraestructura. No se debe afirmar que A ya ejecuta Blender hasta superar la prueba `A_RUNTIME_OK 4.5.3`.
