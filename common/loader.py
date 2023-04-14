import bpy
import os
from .material import add_material, add_material_property


def load_material(path: str, mesh: bpy.types.Mesh):
    if not os.path.exists(path+"/material.txt"):
        return
    with open(path+"/material.txt") as f:
        lines = f.readlines()
        # skip first line
        lines.pop(0)
        for line in lines:
            records = line.split("|")
            if bpy.data.materials.get(records[0]) is None:
                add_material(records[0], records[1], records[2])
            mesh.materials.append(bpy.data.materials[records[0]])


def load_material_property(root_path: str, path: str, mesh: bpy.types.Mesh):
    if not os.path.exists(path+"/material_property.txt"):
        return
    with open(path+"/material_property.txt") as f:
        lines = f.readlines()
        # skip first line
        lines.pop(0)
        for line in lines:
            records = line.split("|")
            add_material_property(
                root_path, records[0], records[1], records[2], records[3])
            if records[1] == "e_TextureDiffuse0" and records[2][-4:] == ".dds" and os.path.exists(root_path+"/"+records[2][:-4]+".txt"):
                with open(root_path+"/"+records[2][:-4]+".txt") as f:
                    anim_data = f.read()
                    material = bpy.data.materials[records[0]]
                    material["anim_data"] = anim_data
                    # iterate anim_data line by line
                    # skip first line
                    lines = anim_data.splitlines()
                    lines.pop(0)
                    lines.pop(0)
                    for line in lines:
                        if records[2] == line:
                            continue
                        if line[-4:] != ".dds":
                            continue
                        line = line[:-4]
                        print("analyzing anim data line "+line)

                        if bpy.data.materials.find(line) == -1:
                            print("adding anim material")
                            # add material
                            add_material(
                                line, records[1], records[2])
                            add_material_property(
                                root_path, line, records[1], line+".dds", records[3])
