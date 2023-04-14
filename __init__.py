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
    "version": (1, 0, 2),
    "blender": (3, 4, 0),
    "location": "File > Export, File > Import",
    "category": "Import-Export",
    "description": "Helper for EverQuest Archives",
}


def export_data(context, filepath: str):
    cmd = bpy.utils.user_resource('SCRIPTS') + "/addons/quail-addon/quail"
    # add suffix based on platform
    if sys.platform == "win32":
        cmd += ".exe"
    if sys.platform == "linux":
        cmd += "-linux"
    if sys.platform == "darwin":
        cmd += "-darwin"

    mode = os.stat(cmd).st_mode
    if mode != 33261:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    pfs_tmp = tempfile.gettempdir() + "/objtemp.obj"

    path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/out/_it13926.eqg"
    start_time = time.time()
    print("Export to path", path)
    eqg_export(path)
    print("Finished in ", time.time() - start_time, " seconds")
    if os.path.exists(pfs_tmp):
        os.remove(pfs_tmp)
    return {'FINISHED'}


def import_data(context, filepath, is_scene_cleared: bool = True, is_scene_modified: bool = True):
    cmd = bpy.utils.user_resource('SCRIPTS') + "/addons/quail-addon/quail"
    # add suffix based on platform
    if sys.platform == "win32":
        cmd += ".exe"
    if sys.platform == "linux":
        cmd += "-linux"
    if sys.platform == "darwin":
        cmd += "-darwin"

    show_message_box()
    mode = os.stat(cmd).st_mode
    if mode != 33261:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # check if file exists
    if not os.path.exists(filepath):
        filepath = filepath.replace(".eqg", ".s3d")

    # get base of filepath
    pfs_tmp = tempfile.gettempdir() + "/" + os.path.basename(filepath)
    start_time = time.time()
    print("Importing data...\n")
    path = ""
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_test.eqg"
    # gnome on a stick
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_it12095.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_sin.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_arena.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_bloodfields.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_it13900.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_omensequip.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_pum_chr.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_zmf.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_xhf.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_shp_chr.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_arena.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_crushbone.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_gequip.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_gequip6.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_it13926.eqg"
    print("quail blender export %s %s" % (filepath, pfs_tmp))
    process = subprocess.run(
        [cmd, "blender", "export", filepath, pfs_tmp])
    if process.returncode != 0:
        if os.path.exists(pfs_tmp):
            shutil.rmtree(pfs_tmp)
        # capture process error
        show_message_box("Failed to process in quail", "Quail Error", 'ERROR')
        return {'CANCELLED'}

    if is_scene_cleared:
        for collection in bpy.data.collections:
            bpy.data.collections.remove(collection)

        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)

        # remove orphed objects
        for obj in bpy.data.objects:
            if obj.users == 0:
                bpy.data.objects.remove(obj)

        for bone in bpy.data.armatures:
            if bone.users == 0:
                bpy.data.armatures.remove(bone)

        # remove orphened materials
        for mat in bpy.data.materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)

        for img in bpy.data.images:
            if img.users == 0:
                bpy.data.images.remove(img)

    if is_scene_modified:
        # bpy.context.space_data.clip_end = 5000
        pass

    if path == "":
        base_name = os.path.basename(filepath)
        path = pfs_tmp+"/_"+base_name
    eqg_import(path)
    s3d_import(path)
    if os.path.exists(pfs_tmp):
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
                           self.filepath)


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
                           self.filepath,
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
