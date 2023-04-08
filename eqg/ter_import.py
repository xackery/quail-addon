import bpy
import os
from ..common.material import add_material, add_material_property


def ter_import(root_path, path) -> bool:
    ext = os.path.splitext(path)[1]
    if ext != ".ter":
        return False

    print("importing ter", path)
    name = os.path.basename(path)
    # trim prefix _ if it exists
    if name[0] == "_":
        name = name[1:]
    base_name = os.path.splitext(name)[0]

    mesh = bpy.data.meshes.new(base_name+"_mesh")

    if os.path.exists(path+"/material.txt"):
        with open(path+"/material.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                add_material(records[0], records[1], records[2])

    if os.path.exists(path+"/material_property.txt"):
        with open(path+"/material_property.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                add_material_property(
                    root_path, records[0], records[1], records[2], records[3])

    vert_mesh = []
    uv_mesh = []
    if os.path.exists(path+"/vertex.txt"):
        with open(path+"/vertex.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                vert_line = records[1].split(",")
                vert_mesh.append((float(vert_line[0]), float(
                    vert_line[1]), float(vert_line[2])))
                uv_line = records[2].split(",")
                uv_mesh.append((float(uv_line[0]), float(uv_line[1])))

    material_mesh = []
    normal_mesh = []
    if os.path.exists(path+"/triangle.txt"):
        with open(path+"/triangle.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                normal_line = records[0].split(",")
                normal_mesh.append((int(normal_line[0]), int(
                    normal_line[1]), int(normal_line[2])))
                material_mesh.append(bpy.data.materials.find(records[2]))

    mesh.from_pydata(vert_mesh, [], normal_mesh)
    # populate mesh polygons
    mesh.update(calc_edges=True)
    # set normal material index
    mesh.polygons.foreach_set("material_index", material_mesh)

    uvlayer = mesh.uv_layers.new(name=base_name+"_uv")
    for vert in mesh.vertices:
        uvlayer.data[vert.index].uv = uv_mesh[vert.index]

    obj = bpy.data.objects.new(base_name, mesh)

    collection = bpy.data.collections.new(name)
    collection.objects.link(obj)
    # put collection in scene
    bpy.context.scene.collection.children.link(collection)
    return True
