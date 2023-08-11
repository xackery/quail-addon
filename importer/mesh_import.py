# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import os
import bmesh
from ..common import string_to_vector, string_to_quaternion
from .bone_import import bone_load, bone_parse


def mesh_import(quail_path: str, mesh_path: str, is_visible: bool) -> bool:
    mesh_name = os.path.basename(mesh_path)
    if mesh_name[0] == "_":
        mesh_name = mesh_name[1:]
    mesh_name = os.path.splitext(mesh_name)[0]  # take off .mesh extension

    print("> Object", mesh_name)
    collection = bpy.data.collections.new(mesh_name)
    # put collection in scene
    bpy.context.scene.collection.children.link(collection)

    if os.path.exists("%s/bone.txt" % mesh_path):
        rig_obj = bone_parse(quail_path, mesh_path,
                             mesh_name, is_visible, collection)
        mesh_obj = mesh_parse(quail_path, mesh_path,
                              mesh_name, is_visible, collection)
        particle_point_parse(quail_path,
                             mesh_path, mesh_name, collection)
        particle_render_parse(quail_path,
                              mesh_path, mesh_name, collection)

        mesh_obj = bpy.context.scene.objects.get(mesh_name)
        mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
        mesh_obj.modifiers["Armature"].object = rig_obj
        mesh_obj.modifiers["Armature"].use_bone_envelopes = True

    else:
        mesh_obj = mesh_parse(quail_path, mesh_path,
                              mesh_name, is_visible, collection)

    # count the number of objects inside the collection
    if len(collection.objects) == 1:
        # if only one object, remove the collection and link the object to the scene
        bpy.context.scene.collection.objects.link(collection.objects[0])
        bpy.data.collections.remove(collection)

    # collection.objects.link(obj)

    # if not is_visible:
    #    bpy.context.view_layer.active_layer_collection.children[mesh_name].hide_viewport = True
    return True


def mesh_parse(quail_path, mesh_path, mesh_name, is_visible, collection) -> bpy.types.Object:
    # == Mesh ==
    mesh = bpy.data.meshes.new(mesh_name+"_mesh")
    print(">> Mesh", mesh_name)
    mesh_verts = []
    mesh_uvs = []

    verts = vertex_load("%s/vertex.txt" % mesh_path)
    for vert in verts:
        mesh_verts.append(
            (vert["position.x"], vert["position.y"], vert["position.z"]))
        # (vert["position.y"], -vert["position.x"], vert["position.z"]))
        mesh_uvs.append((vert["uv.x"], vert["uv.y"]))

    # mesh_uvs.reverse()

    mesh_materials = []
    mesh_normals = []
    mesh_flags = []
    mesh_added_materials = {}

    triangles = triangle_load(mesh, "%s/triangle.txt" % mesh_path)
    for triangle in triangles:
        mesh_normals.append(
            (triangle["index.x"], triangle["index.y"], triangle["index.z"]))
        mesh_flags.append(triangle["flag"])
        idx = bpy.data.materials.find(triangle["material_name"])
        if idx == -1:
            idx = 0
            if len(mesh_added_materials) == 0:
                continue
        if mesh_added_materials.get(idx) == None:
            mesh_added_materials[idx] = True
            mesh.materials.append(bpy.data.materials[idx])
        mesh_materials.append(idx)
    # assign material to mesh
    mesh.from_pydata(mesh_verts, [], mesh_normals)
    mesh.update(calc_edges=True)

    # == UV mapping ==

    uvlayer = mesh.uv_layers.new(name=mesh_name+"_uv")

    # for face in mesh.polygons:
    #    for vert_index, loop_index in zip(face.vertices, face.loop_indices):
    #        uvlayer.data[loop_index] = mesh_uvs[vert_index]

    for triangle in mesh.polygons:
        vertices = list(triangle.vertices)
        i = 0
        for vertex in vertices:
            uvlayer.data[triangle.loop_indices[i]].uv = (mesh_uvs[vertex]
                                                         [0], mesh_uvs[vertex][1]-1)
            i += 1

    # populate mesh polygons
    # set normal material index
    for i in range(len(mesh.polygons)):
        poly = mesh.polygons[i]
        if len(mesh_materials) > i:
            poly.material_index = mesh_materials[i]
        # print(poly.index, poly.material_index, mesh_flags[i])
        # new_map = "flag_%d" % mesh_flags[i]
        # if new_map not in mesh.face_maps:
        #    mesh.face_maps.new(name=new_map)
        # face_map = mesh.face_maps[new_map]
        # bpy.ops.object.face_map_assign()

        # face_map.data. [poly.index].select = True

    faces = {}
    mesh_obj = bpy.data.objects.new(mesh_name, mesh)
    collection.objects.link(mesh_obj)

    for i in range(len(mesh.polygons)):
        poly = mesh.polygons[i]
        if len(mesh_materials) > i:
            poly.material_index = mesh_materials[i]
        new_map = "flag_%d" % mesh_flags[i]
        if new_map not in faces:
            faces[new_map] = []
        face_map = faces[new_map]
        face_map.append(i)

    for face in faces:
        if face not in mesh_obj.face_maps:
            face_map = mesh_obj.face_maps.new(name=face)
        face_map = mesh_obj.face_maps[face]
        face_map.add(faces[face])
        # add custom data to face

    # assign custom data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    flag_layer = bm.faces.layers.float.get("flag")
    if flag_layer is None:
        flag_layer = bm.faces.layers.float.new("flag")

    for face in bm.faces:
        face[flag_layer] = float(mesh_flags[face.index])

    bm.to_mesh(mesh)
    bm.free()

    mesh_obj['ext'] = mesh['ext']
    collection['ext'] = mesh['ext']

    # # parent mesh to root object (rig)
    # if root_obj != None:
    #     mesh_obj.name = mesh_name+"_mesh"
    #     mesh_obj.parent = root_obj
    #     # safe to assume root object is a rig
    #     mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
    #     mesh_obj.modifiers["Armature"].object = root_obj
    #     mesh_obj['ext'] = mesh['ext']
    # else:
    #     mesh.name = mesh_name
    #     root_obj = mesh_obj
    #     root_obj['ext'] = mesh['ext']

    return mesh_obj


def particle_point_parse(quail_path, mesh_path, mesh_name, collection):
    cur_path = "%s/particle_point.txt" % mesh_path
    if not os.path.exists(cur_path):
        return

    # root_bone = arm.bones.find("ROOT_BONE")
    # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    # bpy.ops.object.mode_set(mode='POSE', toggle=False)
    # bpy.context.evaluated_depsgraph_get().update()

    name, points = particle_point_load(cur_path)
    for pt in points:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        print(">> ParticlePoint %s" % pt["name"])
        # create a new empty mesh and the object.
        point = bpy.data.objects.new(name=pt["name"], object_data=None)
        collection.objects.link(point)

        point.empty_display_type = 'PLAIN_AXES'
        point.empty_display_size = 2

        arm = bpy.data.objects['%s_rig' % mesh_name.lower()]
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='EDIT')
        # TODO: fix
        bone_name = pt["bone"]
        point["bone"] = bone_name
        if bone_name == "ATTACH_TO_ORIGIN":
            continue
        bone = arm.data.edit_bones.get(bone_name)
        if bone is None:
            print(">> ParticlePoint %s bone not found" % bone_name)
            continue
        point.location = bone.tail
        # arm.data.edit_bones.active = arm.data.edit_bones[pt["bone"]]
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.select_all(action='DESELECT')
        # point.select_set(True)
        # arm.select_set(True)
        # bpy.context.view_layer.objects.active = arm
        # bpy.ops.object.parent_set(type='BONE', keep_transform=False)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')  # deselect all object
    bpy.context.view_layer.objects.active = None  # remove active object


def particle_render_parse(quail_path, mesh_path, mesh_name, collection):
    cur_path = "%s/particle_render.txt" % mesh_path
    if not os.path.exists(cur_path):
        return

    # root_bone = arm.bones.find("ROOT_BONE")
    # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    # bpy.ops.object.mode_set(mode='POSE', toggle=False)
    # bpy.context.evaluated_depsgraph_get().update()

    renders = particle_render_load(cur_path)
    for rend in renders:
        obj = bpy.context.scene.objects.get(rend["particle_point"])
        if obj is None:
            print(">> ParticleRender %s not found" % rend["particle_point"])
            continue

        prop = obj.get("renders")
        if prop is None:
            prop = []

        prop.append({
            "id": rend["id"],
            "id2": rend["id2"],
            "duration": rend["duration"],
            "unknowna1": rend["unknowna1"],
            "unknowna2": rend["unknowna2"],
            "unknowna3": rend["unknowna3"],
            "unknowna4": rend["unknowna4"],
            "unknowna5": rend["unknowna5"],
            "duration": rend["duration"],
            "unknownb": rend["unknownb"],
            "unknownffffffff": rend["unknownffffffff"],
            "unknownc": rend["unknownc"],
        })
        obj["renders"] = prop


def vertex_load(path: str) -> list:
    verts = []
    r = open(path, "r")
    lines = r.readlines()
    # skip first line
    lines.pop(0)
    for line in lines:
        records = line.split("|")
        pos_line = records[0].split(",")
        norm_line = records[1].split(",")
        uv_line = records[2].split(",")
        uv2_line = records[3].split(",")
        tint_line = records[4].split(",")
        verts.append({
            "position.x": float(pos_line[0]),
            "position.y": float(pos_line[1]),
            "position.z": float(pos_line[2]),
            "normal.x": float(norm_line[0]),
            "normal.y": float(norm_line[1]),
            "normal.z": float(norm_line[2]),
            "uv.x": float(uv_line[0]),
            "uv.y": float(uv_line[1]),
            "uv2.x": float(uv2_line[0]),
            "uv2.y": float(uv2_line[1]),
            "tint.r": float(tint_line[0]),
            "tint.g": float(tint_line[1]),
            "tint.b": float(tint_line[2]),
            "tint.a": float(tint_line[3]),
        })
    r.close()
    return verts


def triangle_load(root_obj, path: str) -> list:
    triangles = []
    with open(path) as f:
        lines = f.readlines()
        # skip first line
        lines.pop(0)
        for line in lines:
            records = line.split("|")
            if records[0] == "ext":
                root_obj["ext"] = records[1].rstrip()
                continue
            index = records[0].split(",")

            triangles.append({
                "index.x": int(index[0]),
                "index.y": int(index[1]),
                "index.z": int(index[2]),
                "flag": int(records[1]),
                "material_name": records[2].rstrip(),
            })
    return triangles


def particle_point_load(path: str) -> tuple[str, list]:
    points = []
    name = os.path.splitext(os.path.basename(path))[0]

    r = open(path, "r")
    lines = r.readlines()
    # skip first line
    lines.pop(0)
    for line in lines:
        records = line.split("|")
        bone = {
            "name": records[0],
            "bone": records[1],
            "translation": string_to_vector(records[2]),
            "rotation": string_to_vector(records[3]),
            "scale": string_to_vector(records[4]),
        }
        points.append(bone)
    r.close()
    return name, points


def particle_render_load(path: str) -> list:
    renders = []
    r = open(path, "r")
    lines = r.readlines()
    # skip first line
    lines.pop(0)
    for line in lines:
        records = line.split("|")
        # id|id2|particle_point|unknowna1|unknowna2|unknowna3|unknowna4|unknowna5|duration|unknownb|unknownffffffff|unknownc
        renders.append({
            "id": int(records[0]),
            "id2": int(records[1]),
            "particle_point": records[2],
            "unknowna1": int(records[3]),
            "unknowna2": int(records[4]),
            "unknowna3": int(records[5]),
            "unknowna4": int(records[6]),
            "unknowna5": int(records[7]),
            "duration": int(records[8]),
            "unknownb": int(records[9]),
            "unknownffffffff": int(records[10]),
            "unknownc": int(records[11]),
        })
    r.close()
    return renders
