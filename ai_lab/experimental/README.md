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

## Preparar y ejecutar

En Linux con `curl` y `tar`:

```bash
chmod +x bootstrap.sh run_headless.sh
./run_headless.sh --python-expr "import bpy; print('Blender:', bpy.app.version_string)"
```

El primer inicio descarga Blender 4.5.3 en la caché local. Las siguientes ejecuciones reutilizan la instalación. El archivo binario no se incluye en el repositorio ni en este paquete comprimido.

## Crear un proyecto transferible

Ejemplo de ejecución de un script de creación:

```bash
./run_headless.sh --python scripts/create_project.py -- /ruta/salida/proyecto.blend
```

Guarda el `.blend` y todos los recursos externos necesarios. Antes de transferirlo, comprueba que el archivo exista, no esté vacío y pueda abrirse con la misma versión de Blender. El destino recomendado en el repositorio es `projects/inbox/`.

## Estado

El launcher y bootstrap están implementados. La ejecución real en un runtime experimental aislado y la transferencia automatizada A → repositorio siguen pendientes de validación.
