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

auto_load.init()

bl_info = {
    "name": "Quail",
    "author": "xackery",
    "version": (1, 0, 1),
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
    obj_tmp = tempfile.gettempdir() + "/objtemp.obj"

    path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/out/_it13926.eqg"
    start_time = time.time()
    print("Export to path", path)
    eqg_export(path)
    print("Finished in ", time.time() - start_time, " seconds")

    return {'FINISHED'}


def import_data(context, filepath):
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

    # get base of filepath
    pfs_tmp = tempfile.gettempdir() + "/" + os.path.basename(filepath)
    print("pfs_tmp", pfs_tmp)

    start_time = time.time()
    print("Importing data...\n")
    # process = subprocess.run([cmd, obj_tmp, filepath, level])
    # if process.returncode == 0:
    #    print("Wrote FLO file", filepath)
    # if os.path.exists(obj_tmp):
    #    os.remove(obj_tmp)

    # remove all collections from scene
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)

    # remove orphed objects
    for obj in bpy.data.objects:
        if obj.users == 0:
            bpy.data.objects.remove(obj)

    for img in bpy.data.images:
        if img.users == 0:
            bpy.data.images.remove(img)

    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    for bone in bpy.data.armatures:
        if bone.users == 0:
            bpy.data.armatures.remove(bone)

    # remove orphened materials
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_arena.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_it13900.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_omensequip.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_it12095.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_pum_chr.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_zmf.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_xhf.eqg"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_shp_chr.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_arena.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_crushbone.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_gequip.s3d"
    # path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_gequip6.s3d"
    path = "/Users/xackery/Documents/code/projects/quail/cmd/blender/test/_it13926.eqg"
    print("Importing path ", path)
    eqg_import(path)
    s3d_import(path)
    print("Finished in ", time.time() - start_time, " seconds")

    return {'FINISHED'}


class ExportQuail(Operator, ExportHelper):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "export_flo.subdiv_data"
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
    bl_idname = "import_flo.subdiv_data"
    bl_label = "Import EQG"

    # ImportHelper mixin class uses this
    filename_ext = ".eqg|.s3d"

    filter_glob: StringProperty(
        default="*.eqg|*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )  # type: ignore

    def execute(self, context):
        return import_data(context,
                           self.filepath)


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
    print("test")
    register()
