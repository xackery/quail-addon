import bpy
import os
from mathutils import Vector, Quaternion
import bmesh


def ani_import(quail_path: str, ani_path: str, mesh_name: str):
    ani_name = os.path.basename(ani_path)
    if ani_name[0] == "_":
        ani_name = ani_name[1:]
    ani_name = os.path.splitext(ani_name)[0]  # take off .ani extension

    print("> Animation", ani_name)
