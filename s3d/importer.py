import bpy
import os
from . import wld_import, mds_import


def s3d_import(s3d_path):
    ext = os.path.splitext(s3d_path)[1]
    if ext != ".s3d":
        return
    print("s3d detected")

    # set visibility of all objects if a zone
    is_visible = True

    for sub_path, dirs, files in os.walk(s3d_path):
        ext = os.path.splitext(sub_path)[1]
        if ext == ".ter":
            is_visible = False
            break
    if is_visible:
        # set clip end to 3000
        # bpy.context.scene.active_clip.end = 3000
        pass

    for sub_path, dirs, files in os.walk(s3d_path):
        print("importing", sub_path)
        if wld_import.wld_import(s3d_path, sub_path, is_visible) and is_visible:
            is_visible = False
        if mds_import.mds_import(s3d_path, sub_path, is_visible) and is_visible:
            is_visible = False
