import bpy
import os
from .material_export import material_export
import bmesh


def mesh_export(quail_path, is_triangulate: bool):

    # for collection in bpy.data.collections:
    #    is_created = False
    for obj in bpy.data.objects:
        mesh_path = "%s/%s.mesh" % (quail_path, obj.name)
        if obj.type != "MESH":
            continue
        os.makedirs(mesh_path)
        mesh_object_export(quail_path, mesh_path,
                           obj.name, obj, is_triangulate)


def mesh_object_export(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):

    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    bm = bmesh.new()
    mesh = obj.to_mesh()
    bm.from_mesh(mesh, face_normals=True, vertex_normals=True)
    if is_triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)  # type: ignore
    bm.faces.ensure_lookup_table()
    bm.normal_update()

    material_export(quail_path, mesh_path, mesh.materials)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    mesh.uv_layers.active = mesh.uv_layers[0]
    mesh.uv_layers.active_index = 0
    mesh.uv_layers[0].active_render = True
    uv = mesh.uv_layers[0].data
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    verts = {}
    print("found %d faces" % len(bm.faces))
    for face in bm.faces:  # type: ignore
        if len(face.verts) != 3:
            print("skipping face with %d verts (want 3)" % len(face.verts))
            continue
        index_str = ""
        # face = bm.faces[face.index]
        for loop in face.loops:
            vert = loop.vert
            index_str += "%d," % vert.index
            line = ""
            line += "%0.8f,%0.8f,%0.8f|" % (vert.co.x, vert.co.y, vert.co.z)
            line += "%0.8f,%0.8f,%0.8f|" % (
                vert.normal.x, vert.normal.y, vert.normal.z)
            line += "%0.8f,%0.8f|" % (uv[loop.index].uv.x, uv[loop.index].uv.y)
            line += "%0.8f,%0.8f|" % (0, 0)
            line += "%d,%d,%d,%d\n" % (120, 120, 120, 255)
            verts[vert.index] = line
        index_str = index_str[:-1]
        tw.write("%s|" % index_str)
        tw.write("%s|%s\n" %
                 (face[flag_layer], mesh.materials[face.material_index].name))

    for vert in verts:
        vw.write(verts[vert])

    vw.close()
    tw.close()
    bm.free()
