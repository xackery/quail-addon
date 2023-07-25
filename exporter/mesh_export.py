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
        mesh_object_export7(quail_path, mesh_path,
                            obj.name, obj, is_triangulate)


def mesh_object_export7(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    mesh = obj.data
    material_export(quail_path, mesh_path, mesh.materials)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    ext = ""
    if len(obj.users_collection) > 0 and obj.users_collection[0].name != "Scene Collection" and obj.users_collection[0].get('ext') != None:
        ext = obj.users_collection[0].get('ext')
    elif obj.get('ext') != None:
        ext = obj.get('ext')
    if ext == "":
        ext = "mod"
    tw.write("ext|%s|-1\n" % ext)

    bm = bmesh.new()
    mesh = obj.data
    bm.from_mesh(mesh, vertex_normals=True, face_normals=True)  # type: ignore
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    uv_layer = bm.loops.layers.uv.active
    col_lay = bm.loops.layers.color.active

    faces = []
    vert_map = {}
    verts = []
    vert_id = 0
    for face in bm.faces:
        pf = []

        material_name = mesh.materials[face.material_index-1].name
        print("material_name", material_name)

        faces.append((pf, face[flag_layer], material_name))
        for loop in face.loops:

            v = map_id = loop.vert

            uv = loop[uv_layer].uv[:]
            map_id = v, uv

            if (_id := vert_map.get(map_id)) is not None:
                pf.append(_id)
                continue

            normal = v.normal
            if col_lay is not None:
                color = tuple(int(x * 255.0) for x in loop[col_lay])
            else:
                color = (128, 128, 128, 255)
            verts.append((v, normal, uv, color))
            vert_map[map_id] = vert_id
            pf.append(vert_id)
            vert_id += 1

    for v, normal, uv, color in verts:
        vw.write("%0.8f,%0.8f,%0.8f|" % (
            v.co[:]))
        vw.write("%0.8f,%0.8f,%0.8f|" % (
            normal[:]))
        vw.write("%0.8f,%0.8f|" % (uv[0], uv[1]+1))
        vw.write("%0.8f,%0.8f|" % (0, 0))
        vw.write("%d,%d,%d,%d\n" % color)

    for indexes, flag, material_name in faces:
        tw.write("%s|" % ",".join(map(str, indexes)))
        tw.write("%s|%s\n" %
                 (flag, material_name))

    vw.close()
    tw.close()


def mesh_object_export6(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    # this is ply route
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    if is_triangulate:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')

    if obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # export as ply
    bpy.ops.export_mesh.ply(filepath="%s/%s.ply" % (mesh_path, mesh_name),
                            use_ascii=True, use_selection=True, use_normals=True)

    mesh = obj.data
    material_export(quail_path, mesh_path, mesh.materials)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    verts = {}
    normals = {}
    uvs = {}
    vertlines = {}
    # load obj file
    r = open("%s/%s.ply" % (mesh_path, mesh_name), "r")
    lines = r.readlines()

    bm = bmesh.new()
    mesh = obj.data
    bm.from_mesh(mesh, vertex_normals=True, face_normals=True)  # type: ignore
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    vert_total = 0
    vert_count = 0
    face_total = 0
    face_count = 0
    is_header_done = False
    for line in lines:
        if line.startswith("element vertex "):
            vert_total = int(line[15:])
            continue
        if line.startswith("element face "):
            face_total = int(line[13:])
            continue
        if line.startswith("end_header"):
            is_header_done = True
            continue
        if not is_header_done:
            continue

        if vert_count < vert_total:
            records = line.split(" ")
            vertlines[vert_count] = ""
            vertlines[vert_count] += "%0.8f,%0.8f,%0.8f|" % (
                float(records[0]), float(records[1]), float(records[2]))
            vertlines[vert_count] += "%0.8f,%0.8f,%0.8f|" % (
                float(records[3]), float(records[4]), float(records[5]))
            vertlines[vert_count] += "%0.8f,%0.8f|" % (
                float(records[6]), float(records[7]))
            vertlines[vert_count] += "%0.8f,%0.8f|" % (0, 0)
            vertlines[vert_count] += "%d,%d,%d,%d\n" % (
                128, 128, 128, 255)
            vw.write(vertlines[vert_count])
            vert_count += 1
            continue
        if face_count < face_total:
            records = line.split(" ")
            face_str = ""
            for record in records[1:]:
                face_str += "%d," % (int(record))
            face_str = face_str[:-1]
            tw.write("%s|" % face_str)
            tw.write("%s|%s\n" %
                     (0, mesh.materials[0].name))
            face_count += 1
            continue

    r.close()
    vw.close()
    tw.close()


def mesh_object_export5(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    # this is obj route
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.export_scene.obj(filepath="%s/%s.obj" % (mesh_path, mesh_name), use_selection=True,
                             use_normals=True, use_uvs=True, use_materials=False, use_triangles=True, use_mesh_modifiers=True)

    mesh = obj.data
    material_export(quail_path, mesh_path, mesh.materials)

    vw = open("%s/vertex.txt" % mesh_path, "w")
    vw.write("position|normal|uv|uv2|tint\n")

    tw = open("%s/triangle.txt" % mesh_path, "w")
    tw.write("index|flag|material_name\n")

    verts = {}
    normals = {}
    uvs = {}
    vertlines = {}
    # load obj file
    r = open("%s/%s.obj" % (mesh_path, mesh_name), "r")
    lines = r.readlines()

    bm = bmesh.new()
    mesh = obj.data
    bm.from_mesh(mesh, vertex_normals=True, face_normals=True)  # type: ignore
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    vert_count = 0
    normal_count = 0
    uv_count = 0
    for line in lines:
        if line.startswith("v "):
            records = line[2:].split(" ")
            verts[vert_count] = (float(records[0]), float(
                records[1]), float(records[2]))
            vert_count += 1
            continue
        if line.startswith("vn "):
            records = line[3:].split(" ")
            normals[normal_count] = (
                float(records[0]), float(records[1]), float(records[2]))
            normal_count += 1
            continue
        if line.startswith("f "):
            records = line[2:].split(" ")
            face_str = ""
            for record in records:
                vert_index = int(record.split("/")[0])-1
                face_str += "%d," % (vert_index)
                vertlines[vert_index] = ""
                vertlines[vert_index] += "%0.8f,%0.8f,%0.8f|" % (
                    verts[vert_index][:])
                normal_index = int(record.split("/")[2])-1
                vertlines[vert_index] += "%0.8f,%0.8f,%0.8f|" % (
                    normals[normal_index][:])
                uv_index = int(record.split("/")[1])-1
                vertlines[vert_index] += "%0.8f,%0.8f|" % (
                    uvs[uv_index][:])
                vertlines[vert_index] += "%0.8f,%0.8f|" % (0, 0)
                vertlines[vert_index] += "%d,%d,%d,%d\n" % (128, 128, 128, 255)
            tw.write("%s|" % face_str[:-1])
            tw.write("%s|%s\n" %
                     (0, mesh.materials[0].name))
            continue
        if line.startswith("vt "):
            records = line[3:].split(" ")
            uvs[uv_count] = (float(records[0]), float(records[1]))
            uv_count += 1
            continue
    for index in vertlines:
        vw.write(vertlines[index])

    r.close()
    vw.close()
    tw.close()


def mesh_object_export4(quail_path: str, mesh_path: str, mesh_name: str, obj: bpy.types.Object, is_triangulate: bool):
    print("> Object", mesh_name)
    print(">> Mesh", mesh_name)

    bm = bmesh.new()
    mesh = obj.data
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
            vert.normal.x. vert.normal.y, vert.normal.z)
        # uv = vert.link_loops[0][uv_layer].uv
        uv = uv_from_vert_average(uv_layer, vert)
        print("Vertex: %r, uv_first=%r, uv_average=%r" %
              (vert, uv_from_vert_first(uv_layer, vert), uv_from_vert_average(uv_layer, vert)))

        vert_str += "%0.8f,%0.8f|" % (
            vert.uvco.x, vert.uvco.y)
        vert_str += "%0.8f,%0.8f|" % (0, 0)
        vert_str += "%d,%d,%d,%d\n" % (128, 128, 128, 255)
        vw.write(vert_str)

    vw.close()
    tw.close()
    bm.free()


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
        # uv = vert.link_loops[0][uv_layer].uv
        uv = uv_from_vert_average(uv_layer, vert)
        print("Vertex: %r, uv_first=%r, uv_average=%r" %
              (vert, uv_from_vert_first(uv_layer, vert), uv_from_vert_average(uv_layer, vert)))

        vert_str += "%0.8f,%0.8f|" % (
            uv.x, uv.y)
        vert_str += "%0.8f,%0.8f|" % (0, 0)
        vert_str += "%d,%d,%d,%d\n" % (128, 128, 128, 255)
        vw.write(vert_str)

    vw.close()
    tw.close()
    bm.free()


def uv_from_vert_first(uv_layer, v):
    for l in v.link_loops:
        uv_data = l[uv_layer]
        return uv_data.uv
    return None


def uv_from_vert_average(uv_layer, v):
    uv_average = Vector((0.0, 0.0))
    total = 0.0
    for loop in v.link_loops:
        uv_average += loop[uv_layer].uv
        total += 1.0

    if total != 0.0:
        return uv_average * (1.0 / total)
    else:
        return None


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
    fw = open("%s/vertex2.txt" % mesh_path, "w")
    me.calc_normals_split()
    me.normals_split_custom_set()

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
                    vert.no.x, vert.no.y, vert.no.z))
                # loops[l_index].normal.x, loops[l_index].normal.y, loops[l_index].normal.z))
                vw.write("%0.8f,%0.8f|" % (vert.uvco.x, vert.uvco.y))
                vw.write("%0.8f,%0.8f|" % (0, 0))
                vw.write("%d,%d,%d,%d\n" % (128, 128, 128, 255))
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
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    mesh.uv_layers.active = mesh.uv_layers[0]
    mesh.uv_layers.active_index = 0
    mesh.uv_layers[0].active_render = True

    # bm.faces.sort(key=lambda f: f.index)

    for face in bm.faces:  # type: ignore
        if len(face.verts) != 3:
            print("skipping face with %d verts (want 3)" % len(face.verts))
            continue
        indexes = [v.index for v in face.verts]
        index_str = ""
        for loop in face.loops:
            vert = loop.vert
            index_str += "%d," % (vert.index)
            vert_str = "%0.8f,%0.8f,%0.8f|" % (
                vert.co.x, vert.co.y, vert.co.z)
            vert_str += "%0.8f,%0.8f,%0.8f|" % (
                vert.normal.x, vert.normal.y, vert.normal.z)
            uv = loop[uv_layer].uv
            vert_str += "%0.8f,%0.8f|" % (
                uv.x, uv.y)
            vert_str += "%0.8f,%0.8f|" % (0, 0)
            vert_str += "%d,%d,%d,%d\n" % (128, 128, 128, 255)
            verts[face.index] = vert_str
        index_str = index_str[:-1]
        tw.write("%s|" % index_str)
        tw.write("%s|%s\n" %
                 (face[flag_layer], mesh.materials[face.material_index].name))

    for vert in verts:
        vw.write(verts[vert])

    vw.close()
    tw.close()
    bm.free()
