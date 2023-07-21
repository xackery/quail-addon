import bpy
import os
import shutil
from .mesh_export import mesh_export


def quail_export(quail_path: str, is_triangulate: bool):
    if os.path.exists(quail_path):
        print("Deleting existing quail path")
        shutil.rmtree(quail_path)

    os.makedirs(quail_path)
    mesh_export(quail_path, is_triangulate)
