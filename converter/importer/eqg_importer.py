import bpy
import os
from ...common.mesh_import import mesh_import


def eqg_import(eqg_path):
    ext = os.path.splitext(eqg_path)[1]
    if ext != ".eqg":
        return

    # set visibility of all objects if a zone
    is_visible = True

    for sub_path, dirs, files in os.walk(eqg_path):
        ext = os.path.splitext(sub_path)[1]
        if ext == ".ter":
            is_visible = False
            break
    if is_visible:
        # set clip end to 3000
        # bpy.context.scene.active_clip.end = 3000
        pass

    for sub_path, dirs, files in os.walk(eqg_path):
        if ext == ".ter":
            is_visible = True
        if mesh_import(eqg_path, sub_path, is_visible) and is_visible:
            is_visible = False
    # turn off edit mode
    # bpy.ops.object.mode_set(mode='OBJECT')
