from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from .. import quail
from ...common import dialogue
import shutil
from . import eqg_exporter as eqg_exporter
from . import s3d_exporter as s3d_exporter

dev_path = ""
# dev_path = "/src/quail/cmd/blender/test/_it13926.eqg"


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

    filter_glob: StringProperty(
        default="*.eqg|*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )  # type: ignore

    def execute(self, context):
        return export_data(context,
                           self.filepath)  # type: ignore


def menu_func_export(self, context):
    self.layout.operator(ExportQuail.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d)")


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
    eqg_exporter.eqg_export(path)

    print("Exporting data...\n")
    if not is_dev:
        is_dev = True
        result = quail.run("import", is_dev, path, filepath, pfs_tmp)
        if result != "":
            # if os.path.exists(pfs_tmp):
            #    print("removing cache")
            #    shutil.rmtree(pfs_tmp)
            msg = "Quail Failed: " + result
            print(msg)
            dialogue.message_box(msg,
                                 "Quail Error", 'ERROR')
            return {'CANCELLED'}

    print("Finished in ", time.time() - start_time, " seconds")
    if os.path.exists(pfs_tmp):
        print("removing cache")
        shutil.rmtree(pfs_tmp)
    return {'FINISHED'}
