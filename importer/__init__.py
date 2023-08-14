# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from ..common import dialog, quail, is_dev
import shutil
from . import quail_import
from bpy_extras.wm_utils.progress_report import ProgressReport


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
    )

    is_scene_cleared: BoolProperty(
        name="Clear Scene Before Import",
        description="Clears the scene before importing, removing all objects, materials, collections etc",
        default=True,
    )

    is_scene_modified: BoolProperty(
        name="Modify Scene for Import",
        description="Sets view clip to 5000 (for large zones), other misc tweaks",
        default=True,
    )

    def execute(self, context):
        return import_data(context,
                           self.filepath,
                           self.is_scene_cleared,
                           self.is_scene_modified)


def menu_func_import(self, context):
    self.layout.operator(ImportQuail.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d)")


def import_data(context, filepath, is_scene_cleared: bool = True, is_scene_modified: bool = True):
    with ProgressReport(context.window_manager) as progress:
        progress.enter_substeps(2, "Generating quail...")
        # check if file exists
        if not os.path.exists(filepath):
            filepath = filepath.replace(".eqg", ".s3d")

        base_name = os.path.basename(filepath)

        # get base of filepath
        pfs_tmp = tempfile.gettempdir() + "/quail/" + base_name + ".quail"
        start_time = time.time()

        result = quail.run("convert", filepath, pfs_tmp)
        if result != "":
            msg = "Quail Failed: " + result
            print(msg)
            dialog.message_box(msg,
                               "Quail Error", 'ERROR')
            return {'CANCELLED'}
        progress.step()

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

            for action in bpy.data.actions:
                bpy.data.actions.remove(action)

        if is_scene_modified:
            # bpy.context.space_data.clip_end = 15000
            pass

        base_name = os.path.basename(filepath)
        path = pfs_tmp

        print("Checking for", path)
        # check if path exists
        if not os.path.exists(path):
            dialog.message_box("File does not exist",
                               "Quail Error", 'ERROR')

        quail_import.quail_import(path)
        for img in bpy.data.images:
            if img.users > 0 and os.path.exists(img.filepath):
                img.pack()

        if os.path.exists(pfs_tmp) and not is_dev():
            print("Removing cache")
            shutil.rmtree(pfs_tmp)

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        print("Full path: %s" % pfs_tmp)
        print("Importing %s took %s seconds" %
              (base_name, time.time() - start_time))
        progress.leave_substeps("Finished!")
        return {'FINISHED'}
