# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import os
from .mesh_import import mesh_import
from .material_import import material_load
from .ani_import import ani_load
from bpy_extras.wm_utils.progress_report import ProgressReport

# qquail import takes a .quail dir and imports it


def quail_import(quail_path):
    with ProgressReport(bpy.context.window_manager) as progress:
        ext = os.path.splitext(quail_path)[1]
        if ext != ".quail":
            return

        # set visibility of all objects if a zone
        is_visible = True

        file_count = 0
        for sub_path, dirs, files in os.walk(quail_path):
            sub_ext = os.path.splitext(sub_path)[1]
            if sub_ext == ".mesh":
                file_count += 1
                continue
            if sub_ext == ".material":
                file_count += 1
                continue
            if sub_ext == ".ani":
                file_count += 1
                continue
        progress.enter_substeps(file_count, "Importing quail...")
        if is_visible:
            # set clip end to 3000
            # bpy.context.scene.active_clip.end = 3000
            pass

        # first load anything that has no refs
        for sub_path, dirs, files in os.walk(quail_path):
            sub_ext = os.path.splitext(sub_path)[1]
            sub_name = os.path.splitext(os.path.basename(sub_path))[0]

            mesh_name = ""
            if sub_path.find(".mesh"):
                dir_base = sub_path.split(".mesh")
                prefix_base = dir_base[0].split(".quail")
                mesh_name = prefix_base[1][1:]
            if sub_ext == ".material":
                print("> Material", sub_name)
                material_load(quail_path, mesh_name, sub_name)
                progress.step()

        # now load ref things
        for sub_path, dirs, files in os.walk(quail_path):
            sub_ext = os.path.splitext(sub_path)[1]
            if sub_ext == ".mesh":
                if mesh_import(quail_path, sub_path, is_visible) and is_visible:
                    is_visible = False
                progress.step()

        # now load ani things
        for sub_path, dirs, files in os.walk(quail_path):
            sub_ext = os.path.splitext(sub_path)[1]
            if sub_ext == ".ani":
                ani_load(quail_path, sub_path)
                progress.step()
    # turn off edit mode
    # bpy.ops.object.mode_set(mode='OBJECT')
