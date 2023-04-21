from .eqg.importer import eqg_import
from .eqg.exporter import eqg_export
from .s3d.importer import s3d_import
from bpy_extras.io_utils import (
    ExportHelper,
    axis_conversion,
)
import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup, Scene
from bpy.utils import register_class, unregister_class
import sys
import tempfile
import subprocess
import os
import stat
from . import auto_load
import time
import shutil
from .common.message_box import show_message_box

auto_load.init()

bl_info = {
    "name": "Quail",
    "author": "xackery",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Export, File > Import",
    "category": "Import-Export",
    "description": "Helper for EverQuest Archives",
}


def quail_run(operation: str, is_dev: bool, arg1: str, arg2: str, pfs_tmp: str) -> str:
    cmd = bpy.utils.user_resource('SCRIPTS') + "/addons/quail-addon/quail"
    if sys.platform == "win32":
        cmd += ".exe"
    if sys.platform == "linux":
        cmd += "-linux"
    if sys.platform == "darwin":
        cmd += "-darwin"

    mode = os.stat(cmd).st_mode
    if mode != 33261:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    verbose = ""
    if is_dev:
        verbose = "-v"
    print("quail blender %s %s %s %s" % (operation, verbose, arg1, arg2))

    args = [cmd, "blender", operation, arg1, arg2]
    if is_dev:
        args = [cmd, "blender", "-v", operation, arg1, arg2]
    process = subprocess.run(
        args, capture_output=True, text=True)
    print(process.stdout)
    if process.returncode == 0:
        return ""
    lines = process.stdout.splitlines()
    if len(lines) > 0:
        return lines[-1]
    return process.stdout


def export_data(context, filepath: str):

    # get base of filepath
    base_name = os.path.basename(filepath)

    pfs_tmp = tempfile.gettempdir() + "/quail/_"+base_name
    path = ""
    # path = "/src/quail/cmd/blender/test/out/_it13926.eqg"
    start_time = time.time()

    is_dev = path != ""
    if not is_dev:
        path = pfs_tmp

    print("Prepping temp data at %s...\n" % pfs_tmp)
    eqg_export(path)

    print("Exporting data...\n")
    if not is_dev:
        is_dev = True
        result = quail_run("import", is_dev, path, filepath, pfs_tmp)
        if result != "":
            # if os.path.exists(pfs_tmp):
            #    print("removing cache")
            #    shutil.rmtree(pfs_tmp)
            msg = "Quail Failed: " + result
            print(msg)
            show_message_box(msg,
                             "Quail Error", 'ERROR')
            return {'CANCELLED'}

    print("Finished in ", time.time() - start_time, " seconds")
    if os.path.exists(pfs_tmp):
        print("removing cache")
        shutil.rmtree(pfs_tmp)
    return {'FINISHED'}


def import_data(context, filepath, is_scene_cleared: bool = True, is_scene_modified: bool = True):

    # check if file exists
    if not os.path.exists(filepath):
        filepath = filepath.replace(".eqg", ".s3d")

    base_name = os.path.basename(filepath)

    # get base of filepath
    pfs_tmp = tempfile.gettempdir() + "/quail/_" + base_name
    start_time = time.time()
    print("Importing %s to %s...\n" % (base_name, pfs_tmp))
    path = ""
    # path = "/src/quail/cmd/blender/test/_test.eqg"
    # gnome on a stick
    # path = "/src/quail/cmd/blender/test/_it12095.eqg"
    # path = "/src/quail/cmd/blender/test/_sin.eqg"
    # path = "/src/quail/cmd/blender/test/_arena.eqg"
    # path = "/src/quail/cmd/blender/test/_bloodfields.eqg"
    # path = "/src/quail/cmd/blender/test/_it13900.eqg"
    # path = "/src/quail/cmd/blender/test/_omensequip.eqg"
    # path = "/src/quail/cmd/blender/test/_pum_chr.s3d"
    # path = "/src/quail/cmd/blender/test/_zmf.eqg"
    # path = "/src/quail/cmd/blender/test/_xhf.eqg"
    # path = "/src/quail/cmd/blender/test/_shp_chr.s3d"
    # path = "/src/quail/cmd/blender/test/_arena.s3d"
    # path = "/src/quail/cmd/blender/test/_crushbone.s3d"
    # path = "/src/quail/cmd/blender/test/_gequip.s3d"
    # path = "/src/quail/cmd/blender/test/_gequip6.s3d"
    # path = "/src/quail/cmd/blender/test/_sin.eqg"
    # path = "/src/quail/cmd/blender/test/_it13926.eqg"

    is_dev = path != ""

    if not is_dev:
        is_dev = True
        result = quail_run("export", is_dev, filepath, pfs_tmp, pfs_tmp)
        if result != "":
            if os.path.exists(pfs_tmp):
                shutil.rmtree(pfs_tmp)
            msg = "Quail Failed: " + result
            print(msg)
            show_message_box(msg,
                             "Quail Error", 'ERROR')
            return {'CANCELLED'}

    if is_scene_cleared:
        for collection in bpy.data.collections:
            bpy.data.collections.remove(collection)

        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)

        # remove orphed objects
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)

        for bone in bpy.data.armatures:
            bpy.data.armatures.remove(bone)

        for mat in bpy.data.materials:
            bpy.data.materials.remove(mat)

        for img in bpy.data.images:
            bpy.data.images.remove(img)

        for bone in bpy.data.armatures:
            bpy.data.armatures.remove(bone)

    if is_scene_modified:
        # bpy.context.space_data.clip_end = 15000
        pass

    if path == "":
        base_name = os.path.basename(filepath)
        path = pfs_tmp+"/_"+base_name

    # check if path exists
    if not os.path.exists(path):
        show_message_box("File does not exist",
                         "Quail Error", 'ERROR')

    eqg_import(path)
    s3d_import(path)
    for img in bpy.data.images:
        if img.users > 0 and os.path.exists(img.filepath):
            img.pack()
    if os.path.exists(pfs_tmp):
        print("removing cache")
        shutil.rmtree(pfs_tmp)
    print("Finished in ", time.time() - start_time, " seconds")

    return {'FINISHED'}


class ExportQuail(Operator, ExportHelper):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "export_quail.subdiv_data"
    bl_label = "Export EQG"

    # ExportHelper mixin class uses this
    filename_ext = ".eqg"

    filter_glob: StringProperty(
        default="*.eqg|*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )  # type: ignore

    def execute(self, context):
        return export_data(context,
                           self.filepath)  # type: ignore


class ImportQuail(Operator, ExportHelper):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "import_quail.subdiv_data"
    bl_label = "Import EQG"

    # ImportHelper mixin class uses this
    filename_ext = ".eqg"

    filter_glob: StringProperty(
        default="*.eqg;*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )  # type: ignore

    is_scene_cleared: BoolProperty(
        name="Clear Scene Before Import",
        description="Clears the scene before importing, removing all objects, materials, collections etc",
        default=True,
    )  # type: ignore

    is_scene_modified: BoolProperty(
        name="Modify Scene for Import",
        description="Sets view clip to 5000 (for large zones), other misc tweaks",
        default=True,
    )  # type: ignore

    def execute(self, context):
        return import_data(context,
                           self.filepath,  # type: ignore
                           self.is_scene_cleared,
                           self.is_scene_modified)


def menu_func_export(self, context):
    self.layout.operator(ExportQuail.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d)")


def menu_func_import(self, context):
    self.layout.operator(ImportQuail.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d)")


def register():
    bpy.utils.register_class(ExportQuail)
    bpy.utils.register_class(ImportQuail)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    auto_load.register()


def unregister():
    bpy.utils.unregister_class(ExportQuail)
    bpy.utils.unregister_class(ImportQuail)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    auto_load.unregister()


if __name__ == "__main__":
    register()
