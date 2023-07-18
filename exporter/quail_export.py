import bpy
import os
import shutil
from .mesh_export import mesh_export


def quail_export(quail_path):
    if os.path.exists(quail_path):
        shutil.rmtree(quail_path)

    os.makedirs(quail_path)
    mesh_export(quail_path)
