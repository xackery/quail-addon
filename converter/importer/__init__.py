from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from .. import quail
from ...common import dialogue
import shutil
from . import eqg_importer as eqg_importer
from . import s3d_importer as s3d_importer

dev_path = ""
# dev_path = "/src/quail/cmd/blender/test/_it13926.eqg"


def register():
    bpy.utils.register_class(ImportQuail)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportQuail)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


class ImportQuail(Operator, ImportHelper):
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


def menu_func_import(self, context):
    self.layout.operator(ImportQuail.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d)")


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
        result = quail.run(
            "export", is_dev, filepath, pfs_tmp, pfs_tmp)
        if result != "":
            if os.path.exists(pfs_tmp):
                shutil.rmtree(pfs_tmp)
            msg = "Quail Failed: " + result
            print(msg)
            dialogue.message_box(msg,
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
        dialogue.message_box("File does not exist",
                             "Quail Error", 'ERROR')

    eqg_importer.eqg_import(path)
    s3d_importer.s3d_import(path)
    for img in bpy.data.images:
        if img.users > 0 and os.path.exists(img.filepath):
            img.pack()
    if os.path.exists(pfs_tmp):
        print("removing cache")
        shutil.rmtree(pfs_tmp)
    print("Finished in ", time.time() - start_time, " seconds")

    return {'FINISHED'}
