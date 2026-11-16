# Experimental Blender Lab — Entorno A

Este paquete es el laboratorio experimental independiente del agente. No es el controlador del Blender de GitHub Actions.

## Responsabilidad

- Ejecutar Blender con `--background`.
- Crear/modificar escenas, objetos, materiales, scripts y proyectos.
- Ejecutar pruebas headless y guardar archivos `.blend`.
- Preparar archivos para transferirlos al repositorio y que Actions los abra en su instancia gráfica separada.

## Aislamiento obligatorio

Este entorno **no** se conecta al AI Bridge, no usa `session_system/repo_headless/client.py`, no consulta ni controla la instancia gráfica de Actions y no necesita una sesión activa de Actions. Su resultado se transfiere como archivo.

El headless del repositorio (Entorno B) tiene una función distinta: controlar la instancia Blender GUI B que corre en Actions. No ejecutar ese cliente desde este laboratorio A.

## Preparar Blender

En Linux con `curl` y `tar`:

```bash
chmod +x bootstrap.sh run_headless.sh
./run_headless.sh --python-expr "import bpy; print('Blender:', bpy.app.version_string)"
```

El primer inicio descarga Blender 4.5.3 en la caché local. Las siguientes ejecuciones reutilizan la instalación. El archivo binario no se incluye en el repositorio ni en este paquete comprimido.

## Generar una escena de validación en A

```bash
./run_headless.sh --python "$PWD/scripts/create_validation_scene.py" -- "$PWD/output/validation-scene.blend"
```

El script crea una escena con suelo, cubo, esfera, toroide, rótulo, cámara y luces. Guarda el proyecto `.blend` y renderiza una imagen PNG junto a él. Es una escena de diagnóstico deliberadamente reconocible para comprobar que B abrió el archivo correcto y que el render no está vacío.

Valida el archivo desde el propio Blender headless A:

```bash
./run_headless.sh "$PWD/output/validation-scene.blend" --python "$PWD/scripts/validate_project.py"
```

La validación comprueba la ruta del proyecto, la cámara y los objetos de prueba esperados.

## Transferir a B

1. Comprueba que el `.blend` y su PNG existan y tengan tamaño no nulo.
2. Sube/versiona el proyecto bajo `projects/inbox/` en el repositorio.
3. Abre **Actions → Blender GUI Session → Run workflow**.
4. En `project_path`, indica la ruta exacta del `.blend`, por ejemplo `projects/inbox/validation-scene.blend`.
5. Actions abre ese archivo en su propia instancia Blender GUI B para inspección.

No copies el ejecutable de Blender al repositorio. Los proyectos deben ser pequeños, versionados y transferidos explícitamente.

## Estado

El bootstrap, launcher y generador de escena están implementados. No se ha podido ejecutar Blender en este runtime de trabajo porque no dispone del binario ni de acceso de red al distribuidor. Por eso el generador todavía requiere una ejecución real en un entorno que tenga Blender instalado. La transferencia automatizada A → repositorio y el control remoto desde el agente siguen pendientes.
