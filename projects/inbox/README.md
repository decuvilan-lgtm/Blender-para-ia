# Blender project inbox

Place validated `.blend` files created in the independent experimental environment A here.

## Handoff contract

- Keep each generated project as a versioned file; do not overwrite a previous experiment without checking its history.
- Include external assets required by the scene, or pack them into the `.blend` before transfer.
- Validate the project in environment A before committing it.
- Start the **Blender GUI Session** workflow and set `project_path` to the exact repository-relative path, for example `projects/inbox/validation-scene.blend`.
- Actions opens that file in its separate GUI instance B. The controller and Bridge in B inspect it and produce evidence.

No project binary is included in this directory yet. The directory is the designated handoff location.
