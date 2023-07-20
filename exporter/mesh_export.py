import bpy
import os
from .material_export import material_export


def mesh_export(quail_path):

    # for collection in bpy.data.collections:
    #    is_created = False
    for obj in bpy.data.objects:
        mesh_path = "%s/%s.mesh" % (quail_path, obj.name)
        if obj.type != "MESH":
            continue
        os.makedirs(mesh_path)
        mesh_object_export(quail_path, mesh_path, obj.name, obj)


def mesh_object_export(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object):
    mesh = obj.to_mesh()
    material_export(quail_path, mesh_path, mesh.materials)
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)
    with open("%s/vertex.txt" % mesh_path, "w") as vw:
        vw.write("position|normal|uv|uv2|tint\n")
        mesh.uv_layers.active = mesh.uv_layers[0]
        mesh.uv_layers.active_index = 0
        mesh.uv_layers[0].active_render = True
        uv = mesh.uv_layers[0].data
        for i in range(len(mesh.vertices)):
            vert = mesh.vertices[i]
            # position
            vw.write("%0.8f,%0.8f,%0.8f|" %
                     (vert.co.x, vert.co.y, vert.co.z))  # type: ignore
            # normal
            vw.write("%0.8f,%0.8f,%0.8f|" %
                     (vert.normal.x, vert.normal.y, vert.normal.z))  # type: ignore
            # uv
            vw.write("%0.8f,%0.8f|" %
                     (uv[i].uv.x, uv[i].uv.y))  # type: ignore
            # uv 2
            vw.write("%0.8f,%0.8f|" %
                     (0, 0))
            # tint
            vw.write("%d,%d,%d,%d\n" %
                     (120, 120, 120, 255))

    with open("%s/triangle.txt" % mesh_path, "w") as tw:
        tw.write("index|flag|material_name\n")
        for poly in mesh.polygons:
            flag = 0

            if len(mesh.face_maps) > 0 and len(mesh.face_maps[0].data) >= poly.index:
                name = obj.face_maps[mesh.face_maps[0].data[poly.index].value].name
                flag = name[5:]
            tw.write("%d,%d,%d|%s|%s\n" % (
                poly.vertices[0], poly.vertices[1], poly.vertices[2], flag, mesh.materials[poly.material_index].name))
