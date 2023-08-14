# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from ..common import dialog, quail
import shutil
from . import quail_export as quail_export


def register():
    bpy.utils.register_class(ExportQuail)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportQuail)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


class ExportQuail(Operator, ExportHelper):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "export_quail.subdiv_data"
    bl_label = "Export EQG"

    # ExportHelper mixin class uses this
    filename_ext = ".eqg"

    is_triangulate: BoolProperty(
        name="Triangulate",
        description="Triangulate Meshes",
        default=False,
    )

    filter_glob: StringProperty(
        default="*.eqg|*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        if export_data(context,
                       self.filepath, self.is_triangulate):
            return {'FINISHED'}
        return {'CANCELLED'}


def menu_func_export(self, context):
    self.layout.operator(ExportQuail.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d)")


def export_data(context, filepath: str, is_triangulate: bool) -> bool:
    start_time = time.time()

    material_count = 0
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        for slot in obj.material_slots:
            if slot.material:
                material_count += 1
                break
        if material_count > 1:
            break

    if material_count == 0:
        dialog.message_box("No materials found in scene. Please assign a material to at least one object.",
                           "Quail Error", 'ERROR')
        return False

    # get base of filepath
    base_name = os.path.basename(filepath)

    base_name = os.path.splitext(base_name)[0]

    pfs_tmp = tempfile.gettempdir() + "/quail/"+base_name + ".quail"

    print("Prepping temp data at %s" % pfs_tmp)
    if not quail_export.quail_export(pfs_tmp, is_triangulate):
        return False

    result = quail.run("convert", pfs_tmp, filepath)
    if result != "":
        msg = "Quail Failed: " + result
        print(msg)
        dialog.message_box(msg,
                           "Quail Error", 'ERROR')
        return False

    if os.path.exists(pfs_tmp):
        print("Removing cache")
        # shutil.rmtree(pfs_tmp)
    # remove orphened scene materials
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)

    print("Finished in ", time.time() - start_time, " seconds")
    return True
