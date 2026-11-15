# Experimental Blender Lab

Este directorio contiene el punto de entrada reproducible del laboratorio experimental.

El paquete descargable de Actions incluye este directorio y el cliente Bridge. No incluye una copia de 1+ GB del ejecutable Blender: el bootstrap descarga la versión fijada desde el distribuidor oficial en el runner.

## Uso

Consulta `bootstrap.sh` para preparar Blender y `session_system/repo_headless/client.py` para enviar operaciones al Blender activo.

## Ejecutar Blender en modo headless

En Linux con `curl` y `tar` instalados:

```bash
chmod +x bootstrap.sh run_headless.sh
./run_headless.sh --python-expr "import bpy; print('Blender:', bpy.app.version_string)"
```

El primer inicio descarga y extrae Blender 4.5.3 en la caché local. Las siguientes ejecuciones reutilizan esa instalación. El modo experimental es independiente de la sesión gráfica de GitHub Actions.
