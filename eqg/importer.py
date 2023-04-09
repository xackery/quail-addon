import bpy
import os
from . import mds_import, ter_import, mod_import


def eqg_import(eqg_path):
    ext = os.path.splitext(eqg_path)[1]
    if ext != ".eqg":
        return
    print("eqg detected")

    # set visibility of all objects if a zone
    is_visible = True

    for sub_path, dirs, files in os.walk(eqg_path):
        ext = os.path.splitext(sub_path)[1]
        if ext == ".ter" or ext == ".zon":
            is_visible = False
            break
    if is_visible:
        # set clip end to 3000
        # bpy.context.scene.active_clip.end = 3000
        pass

    for sub_path, dirs, files in os.walk(eqg_path):
        if ter_import.ter_import(eqg_path, sub_path) and is_visible:
            is_visible = False
        if mds_import.mds_import(eqg_path, sub_path, is_visible) and is_visible:
            print("hiding future")
            is_visible = False
        if mod_import.mod_import(eqg_path, sub_path, is_visible) and is_visible:
            is_visible = False
