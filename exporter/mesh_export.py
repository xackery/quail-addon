import bpy
import os

from mathutils import Vector
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
        mesh_object_export4(quail_path, mesh_path,
                            obj.name, obj, is_triangulate)


def mesh_object_export4(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)


def mesh_object_export3(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    bm = bmesh.new()
    mesh = obj.data
    # mesh.calc_normals_split()
    # mesh.flip_normals()
    # mesh.calc_normals_split()
    bm.from_mesh(mesh, vertex_normals=True, face_normals=True)  # type: ignore
    if is_triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)  # type: ignore
    bm.normal_update()

    material_export(quail_path, mesh_path, mesh.materials)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    mesh.uv_layers.active = mesh.uv_layers[0]
    mesh.uv_layers.active_index = 0
    mesh.uv_layers[0].active_render = True
    uv_layer = bm.loops.layers.uv.active

    vert_indexes = {}
    for face in bm.faces:  # type: ignore
        if len(face.verts) != 3:
            print("skipping face with %d verts (want 3)" % len(face.verts))
            continue
        indexes = [v.index for v in face.verts]
        # indexes.sort()
        index_str = "%d,%d,%d" % (
            indexes[0], indexes[1], indexes[2])

        tw.write("%s|" % index_str)
        tw.write("%s|%s\n" %
                 (face[flag_layer], mesh.materials[face.material_index].name))
        vert_indexes[indexes[0]] = True
        vert_indexes[indexes[1]] = True
        vert_indexes[indexes[2]] = True
        # face.loop_indices.sort()

        # face.uv_textures.active = face.uv_layers[0]

    for vert in bm.verts:  # type: ignore
        if vert.index not in vert_indexes:
            continue
        vert_str = "%0.8f,%0.8f,%0.8f|" % (
            vert.co.x, vert.co.y, vert.co.z)
        vert_str += "%0.8f,%0.8f,%0.8f|" % (
            vert.normal.x, vert.normal.y, vert.normal.z)
        uv = vert.link_loops[0][uv_layer].uv
        vert_str += "%0.8f,%0.8f|" % (
            uv.x, uv.y)
        vert_str += "%0.8f,%0.8f|" % (0, 0)
        vert_str += "%d,%d,%d,%d\n" % (128, 128, 128, 255)
        vw.write(vert_str)

    vw.close()
    tw.close()
    bm.free()


def mesh_object_export2(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    me = obj.data

    material_export(quail_path, mesh_path, me.materials)
    face_index_pairs = [(face, index)
                        for index, face in enumerate(me.polygons)]

    def sort_func(a): return (a[0].material_index, a[0].use_smooth)
    face_index_pairs.sort(key=sort_func)
    me_verts = me.vertices[:]
    loops = me.loops
    fw = open("%s/vertex.txt" % mesh_path, "w")
    me.calc_normals_split()

    # uv export
    uv = f_index = uv_index = uv_key = uv_val = uv_ls = None
    uv_face_mapping = [None] * len(face_index_pairs)
    uv_dict = {}
    uv_get = uv_dict.get
    uv_layer = me.uv_layers.active.data[:]
    uv_unique_count = no_unique_count = 0

    for f, f_index in face_index_pairs:
        uv_ls = uv_face_mapping[f_index] = []
        for uv_index, l_index in enumerate(f.loop_indices):
            uv = uv_layer[l_index].uv
            # include the vertex index in the key so we don't share UV's between vertices,
            # allowed by the OBJ spec but can cause issues for other importers, see: T47010.

            # this works too, shared UV's for all verts
            # ~ uv_key = veckey2d(uv)
            uv_key = loops[l_index].vertex_index, veckey2d(uv)

            uv_val = uv_get(uv_key)
            if uv_val is None:
                vert = me_verts[loops[l_index].vertex_index]
                vw.write("%0.8f,%0.8f,%0.8f|" % (
                    vert.co.x, vert.co.y, vert.co.z))
                vw.write("%0.8f,%0.8f,%0.8f|" % (
                    loops[l_index].normal.x, loops[l_index].normal.y, loops[l_index].normal.z))
                uv_val = uv_dict[uv_key] = uv_unique_count
            uv_ls.append(uv_val)

    for f, f_index in face_index_pairs:
        f_smooth = f.use_smooth

        f_v = [(vi, me_verts[v_idx], l_idx)
               for vi, (v_idx, l_idx) in enumerate(zip(f.vertices, f.loop_indices))]
        if len(f_v) != 3:
            print("skipping face with %d verts (want 3)" % len(f_v))
            continue
        fw.write('f')
        index_str = ""
        for vi, v, li in f_v:
            index_str += "%d," % (v.index)
            fw.write(" %s" % v.index)
        index_str = index_str[:-1]
        tw.write("%s|" % index_str)
        tw.write("%s|%s\n" % (0,
                              me.materials[f.material_index].name))
        fw.write('\n')
    fw.close()
    vw.close()
    tw.close()


def veckey2d(v):
    return round(v[0], 4), round(v[1], 4)


def mesh_object_export(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):

    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    bm = bmesh.new()
    mesh = obj.to_mesh()
    # mesh.flip_normals()
    # mesh.calc_normals_split()
    bm.from_mesh(mesh)  # , face_normals=True, vertex_normals=True)
    if is_triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)  # type: ignore
    bm.normal_update()

    material_export(quail_path, mesh_path, mesh.materials)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    uv_layer = bm.loops.layers.uv.verify()
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    verts = {}
    # bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    mesh.uv_layers.active = mesh.uv_layers[0]
    mesh.uv_layers.active_index = 0
    mesh.uv_layers[0].active_render = True

    bm.faces.sort(key=lambda f: f.index)

    for face in bm.faces:  # type: ignore
        if len(face.verts) != 3:
            print("skipping face with %d verts (want 3)" % len(face.verts))
            continue
        indexes = [v.index for v in face.verts]
        index_str = "%d,%d,%d" % (
            indexes[0], indexes[1], indexes[2])
        for loop in face.loops:
            vert = loop.vert
            vert_str = "%0.8f,%0.8f,%0.8f|" % (
                vert.co.x, vert.co.y, vert.co.z)
            vert_str += "%0.8f,%0.8f,%0.8f|" % (
                face.normal.x, face.normal.y, face.normal.z)
            vert_str += "%0.8f,%0.8f|" % (
                loop[uv_layer].uv.x, loop[uv_layer].uv.y)
            vert_str += "%0.8f,%0.8f|" % (0, 0)
            vert_str += "%d,%d,%d,%d\n" % (128, 128, 128, 255)
            verts[vert.index] = vert_str

        tw.write("%s|" % index_str)
        tw.write("%s|%s\n" %
                 (face[flag_layer], mesh.materials[face.material_index].name))

    for vert in verts:
        vw.write(verts[vert])

    vw.close()
    tw.close()
    bm.free()
