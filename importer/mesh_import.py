import bpy
import os
from mathutils import Vector, Quaternion
import bmesh


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
        root_obj = bone_parse(quail_path, mesh_path,
                              mesh_name, is_visible, collection, None)
        root_obj = mesh_parse(quail_path, mesh_path,
                              mesh_name, is_visible, collection, root_obj)
        particle_point_parse(quail_path,
                             mesh_path, mesh_name, collection, root_obj)
        particle_render_parse(quail_path,
                              mesh_path, mesh_name, collection, root_obj)
    else:
        root_obj = mesh_parse(quail_path, mesh_path,
                              mesh_name, is_visible, collection, None)
    # count the number of objects inside the collection
    if len(collection.objects) == 1:
        # if only one object, remove the collection and link the object to the scene
        bpy.context.scene.collection.objects.link(collection.objects[0])
        bpy.data.collections.remove(collection)

    # collection.objects.link(obj)

    # if not is_visible:
    #    bpy.context.view_layer.active_layer_collection.children[mesh_name].hide_viewport = True
    return True


def mesh_parse(quail_path, mesh_path, mesh_name, is_visible, collection, root_obj) -> bpy.types.Object:
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

    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    for face in bm.faces:
        face[flag_layer] = mesh_flags[face.index]

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
    #     mesh_obj.modifiers["Armature"].object = root_obj  # type: ignore
    #     mesh_obj['ext'] = mesh['ext']
    # else:
    #     mesh.name = mesh_name
    #     root_obj = mesh_obj
    #     root_obj['ext'] = mesh['ext']

    return root_obj


def bone_parse(quail_path, mesh_path, mesh_name, is_visible, collection, root_obj) -> bpy.types.Object:
    cur_path = "%s/bone.txt" % mesh_path

    print(">> Bone", mesh_name)
    arm = bpy.data.armatures.new(name=mesh_name+"_armature")
    # bpy.context.scene.collection.objects.link(arm)
    rig_name = mesh_name+"_rig"
    rig_obj = bpy.data.objects.new(rig_name, arm)
    collection.objects.link(rig_obj)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.editmode_toggle()

    bone_obj = bpy.data.objects.new(name="root", object_data=arm)

    bones = bone_load(cur_path)

    # collection.objects.link(bone_obj)

    if not bones:
        return rig_obj

    for i, bone in enumerate(bones):
        print("Bone: %s" % bone['name'])

        bone_obj = arm.edit_bones.new(name=bone['name'])
        bone['ref'] = bone_obj
        if i == 0:
            bone_obj.head = (0, 0, 0)
            bone_obj.tail = bone['pivot']

    traverse_bone(bones, bones[0])

    # find all bones with

    # name|child_index|children_count|next|pivot|rotation|scale
    # child_next_index = int(bone_line[1])
    # children_count = int(bone_line[2])
    # next_index = int(bone_line[3])
    # position = bone_line[4].split(",")
    # position = (float(position[0]), float(position[1]), float(position[2]))
    # quad = bone_line[5].split(",")
    # quad = (float(quad[0]), float(quad[1]), float(quad[2]), float(quad[3]))
    # current_bone = arm.edit_bones.new(name=bone_line[0])
    # current_bone.head = position

    # if next_index == -1 and children_count > 0:
    #     bone_line = bones[child_next_index]
    #     bone_line = bone_line.split("|")
    #     child_next_index = int(bone_line[1])
    #     children_count = int(bone_line[2])
    #     next_index = int(bone_line[3])
    #     position = bone_line[4].split(",")
    #     position = (float(position[0]), float(position[1]), float(position[2]))
    #     quad = bone_line[5].split(",")
    #     quad = (float(quad[0]), float(quad[1]), float(quad[2]), float(quad[3]))
    #     current_bone.tail = position
    #     # quat_arm_space = Quaternion(quad)
    #     # current_bone.transform(quat_arm_space.to_matrix())
    #     # current_bone.translate(position)
    #     next_bone = arm.edit_bones.new(name=bone_line[0])
    #     next_bone.head = position
    #     next_bone.parent = current_bone
    #     current_bone = next_bone

    #     if next_index > 0:
    #         bone_line = bones[child_next_index]
    #         bone_line = bone_line.split("|")
    #         child_next_index = int(bone_line[1])
    #         children_count = int(bone_line[2])
    #         next_index = int(bone_line[3])
    #         next_bone = arm.edit_bones.new(name=bone_line[0])
    #         next_position = bone_line[4].split(",")
    #         next_position = (float(next_position[0]), float(
    #             next_position[1]), float(next_position[2]))
    #         next_quad = bone_line[5].split(",")
    #         next_quad = (float(next_quad[0]), float(quad[1]),
    #                      float(next_quad[2]), float(next_quad[3]))
    #         next_bone.head = (position[0]+next_position[0], position[1] +
    #                           next_position[1], position[2]+next_position[2])
    #         next_bone.parent = current_bone
    # if root_obj != None:
    #     bone_obj.parent = root_obj
    # else:
    #     root_obj = rig_obj

#         bpy.ops.object.mode_set(mode='EDIT', toggle=False)
#         parent_bone_quad_arm_space = Quaternion((1, 0, 0, 0))

#         for i, line in enumerate(lines):
#             records = line.split("|")
#             current_bone = arm.edit_bones.new(name=records[0])

#             position = records[4].split(",")
#             position = (float(position[0]), float(
#                 position[1]), float(position[2]))
#             quad = records[5].split(",")
#             quad = (float(quad[0]), float(quad[1]),
#                     float(quad[2]), float(quad[3]))
#             pivot_line = records[4].split(",")
#             current_bone.head = (0, 0, 0)
#             current_bone.tail = (float(pivot_line[0]), float(
#                 pivot_line[1]), float(pivot_line[2]))

#             if i == 0:
#                 quat_arm_space = Quaternion(quad)
#                 current_bone.transform(quat_arm_space.to_matrix())
#                 current_bone.translate(position)
#                 parent_bone = current_bone
#                 parent_bone_tail = current_bone.tail
#                 parent_bone_quad_arm_space = quat_arm_space
#             else:
#                 quat_arm_space = Quaternion(quad)
#                 transform_quat = parent_bone_quad_arm_space @ quat_arm_space
#                 current_bone.transform(quat_arm_space.to_matrix())
#                 current_bone.translate(position)
#                 current_bone.parent = parent_bone
#                 parent_bone = current_bone
#                 parent_bone_tail = current_bone.tail
#                 parent_bone_quad_arm_space = quat_arm_space
    return root_obj


def traverse_bone(bones: list, bone: dict):
    bone_cur = bone['ref']
    if bone['children_count'] > 0:
        bone_sel = bones[bone['child_index']]
        bone_sel['ref'].parent = bone_cur
        bone_sel['ref'].head = bone_cur.tail
        bone_sel['ref'].tail = bone_sel['pivot']

        traverse_bone(bones, bones[bone['child_index']])
    if bone['next'] > -1:
        bone_sel = bones[bone['next']]
        bone_sel['ref'].parent = bone_cur.parent
        bone_sel['ref'].head = bone_cur.parent.tail
        bone_sel['ref'].tail = bone_sel['pivot']
        traverse_bone(bones, bones[bone['next']])

        # bone_sel['ref'].translate(bone_sel['pivot'])


def particle_point_parse(quail_path, mesh_path, mesh_name, collection, root_obj):
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

        arm = bpy.data.objects['%s_rig' % mesh_name]
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='EDIT')
        # TODO: fix
        bone_name = pt["bone"]
        point["bone"] = bone_name
        if bone_name != "ATTACH_TO_ORIGIN":
            bone = arm.data.edit_bones[bone_name]
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


def particle_render_parse(quail_path, mesh_path, mesh_name, collection, root_obj):
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


def string_to_vector(line: str) -> Vector:
    lines = line.split(",")
    return Vector((float(lines[0]), float(lines[1]), float(lines[2])))


def string_to_quaternion(line: str) -> Quaternion:
    lines = line.split(",")
    return Quaternion((float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3])))


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
                print("ext loaded as %s" % records[1].rstrip())
                print("setting %s as ext" % root_obj.name)
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


def bone_load(path: str) -> list:
    bones = []
    with open(path) as f:
        lines = f.readlines()
        # skip first line
        lines.pop(0)
        for line in lines:
            records = line.split("|")
            bone = {
                "name": records[0],
                "child_index": int(records[1]),
                "children_count": int(records[2]),
                "next": int(records[3]),
                "pivot": string_to_vector(records[4]),
                "rotation": string_to_quaternion(records[5]),
                "scale": string_to_vector(records[6]),
            }
            # x = bone["pivot"].x
            # bone["pivot"].x = bone["pivot"].y
            # bone["pivot"].y = -x
            bones.append(bone)
    return bones


def particle_point_load(path: str) -> tuple[str, list]:
    points = []
    name = os.path.splitext(os.path.basename(path))[0]

    r = open(path, "r")
    lines = r.readlines()
    # skip first line
    lines.pop(0)
    for line in lines:
        records = line.split("|")
        points.append({
            "name": records[0],
            "bone": records[1],
            "translation": string_to_vector(records[2]),
            "rotation": string_to_vector(records[3]),
            "scale": string_to_vector(records[4]),
        })
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
