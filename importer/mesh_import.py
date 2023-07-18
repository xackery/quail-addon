import bpy
import os
from mathutils import Vector, Quaternion


def mesh_import(quail_path, mesh_path, is_visible) -> bool:
    mesh_name = os.path.basename(mesh_path)
    if mesh_name[0] == "_":
        mesh_name = mesh_name[1:]
    mesh_name = os.path.splitext(mesh_name)[0]  # take off .mesh extension

    print("> Object", mesh_name)
    # collection = bpy.data.collections.new(mesh_name)
    # put collection in scene
    # bpy.context.scene.collection.children.link(collection)

    if os.path.exists("%s/bone.txt" % mesh_path):
        root_obj = bone_parse(quail_path, mesh_path,
                              mesh_name, is_visible, None)
        root_obj = mesh_parse(quail_path, mesh_path,
                              mesh_name, is_visible, root_obj)
        particle_point_parse(quail_path, mesh_path, mesh_name, root_obj)
    else:
        root_obj = mesh_parse(quail_path, mesh_path,
                              mesh_name, is_visible, None)
    # collection.objects.link(obj)

    # if not is_visible:
    #    bpy.context.view_layer.active_layer_collection.children[mesh_name].hide_viewport = True
    return True


def mesh_parse(quail_path, mesh_path, mesh_name, is_visible, root_obj) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(mesh_name+"_mesh")
    print(">> Mesh", mesh_name)
    mesh_verts = []
    mesh_uvs = []
    cur_path = "%s/vertex.txt" % mesh_path
    if os.path.exists(cur_path):
        with open(cur_path) as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                vert_line = records[0].split(",")
                mesh_verts.append((float(vert_line[0]), float(
                    vert_line[1]), float(vert_line[2])))
                uv_line = records[2].split(",")
                mesh_uvs.append((float(uv_line[0]), float(uv_line[1])))
    # uv_mesh.reverse()

    mesh_materials = []
    mesh_normals = []
    mesh_flags = []
    cur_path = "%s/triangle.txt" % mesh_path
    mesh_added_materials = {}
    if os.path.exists(cur_path):
        with open(cur_path) as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                normal_line = records[0].split(",")
                mesh_normals.append((int(normal_line[0]), int(
                    normal_line[1]), int(normal_line[2])))
                mesh_flags.append(int(records[1]))
                idx = bpy.data.materials.find(records[2].rstrip())
                if idx == -1:
                    # print("Could not find material: " + records[2].rstrip())
                    idx = 0
                    if len(mesh_added_materials) == 0:
                        continue
                # print(records[2].rstrip()+": " +
                #      str(bpy.data.materials.find(records[2].rstrip())))
                if mesh_added_materials.get(idx) == None:
                    mesh_added_materials[idx] = True
                    mesh.materials.append(bpy.data.materials[idx])
                mesh_materials.append(idx)

    # assign material to mesh
    mesh.from_pydata(mesh_verts, [], mesh_normals)
    mesh.update(calc_edges=True)

    uvlayer = mesh.uv_layers.new(name=mesh_name+"_uv")
    # for vert in mesh.vertices:
    # print(vert.co, vert.index, mesh_uvs[vert.index])
    # uvlayer.data[vert.index].uv = mesh_uvs[vert.index]

    # for face in mesh.polygons:
    #    for vert_index, loop_index in zip(face.vertices, face.loop_indices):
    #        uvlayer.data[loop_index] = mesh_uvs[vert_index]

    for triangle in mesh.polygons:
        vertices = list(triangle.vertices)
        i = 0
        index = triangle.loop_indices[i]
        for vertex in vertices:
            uvlayer.data[index].uv = mesh_uvs[vertex]
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
    bpy.context.scene.collection.objects.link(mesh_obj)
    for i in range(len(mesh.polygons)):
        poly = mesh.polygons[i]
        if len(mesh_materials) > i:
            poly.material_index = mesh_materials[i]
        new_map = "flag_%d" % mesh_flags[i]
        if new_map not in faces:
            faces[new_map] = []
        face_map = faces[new_map]
        face_map.append(i)

    for key in faces:
        if key not in mesh_obj.face_maps:
            face_map = mesh_obj.face_maps.new(name=key)
        face_map = mesh_obj.face_maps[key]
        face_map.add(faces[key])

    if root_obj != None:
        mesh_obj.name = mesh_name+"_mesh"
        mesh_obj.parent = root_obj
        # safe to assume root object is a rig
        mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
        mesh_obj.modifiers["Armature"].object = root_obj  # type: ignore
    else:
        mesh.name = mesh_name
        root_obj = mesh_obj

    return root_obj


def bone_parse(quail_path, mesh_path, mesh_name, is_visible, root_obj) -> bpy.types.Object:
    cur_path = "%s/bone.txt" % mesh_path

    print(">> Bone", mesh_name)
    arm = bpy.data.armatures.new(name=mesh_name+"_armature")
    # bpy.context.scene.collection.objects.link(arm)
    rig_name = mesh_name+"_rig"
    if root_obj == None:
        rig_name = mesh_name
    rig_obj = bpy.data.objects.new(rig_name, arm)
    bpy.context.scene.collection.objects.link(rig_obj)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.editmode_toggle()

    bone_obj = bpy.data.objects.new(name="root", object_data=arm)

    bones = []

    # collection.objects.link(bone_obj)

    with open(cur_path) as f:
        lines = f.readlines()
        lines.pop(0)
        for _, line in enumerate(lines):
            records = line.split("|")
            bones.append({'name': records[0], 'child_index': int(records[1]), 'children_count': int(records[2]), 'next': int(records[3]), 'pivot': string_to_vector(
                records[4]), 'rotation': string_to_quaternion(records[5]), 'scale': string_to_vector(records[6])})
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


def particle_point_parse(quail_path, mesh_path, mesh_name, root_obj):
    cur_path = "%s/particle_point.txt" % mesh_path
    if not os.path.exists(cur_path):
        return

    # root_bone = arm.bones.find("ROOT_BONE")
    # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    # bpy.ops.object.mode_set(mode='POSE', toggle=False)
    # bpy.context.evaluated_depsgraph_get().update()

    with open(cur_path) as f:
        lines = f.readlines()
        lines.pop(0)
        for _, line in enumerate(lines):
            # deselect all

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            records = line.split("|")
            print(">> ParticlePoint %s" % records[0])
            # create a new empty mesh and the object.
            point = bpy.data.objects.new(name=records[0], object_data=None)
            bpy.context.collection.objects.link(point)

            point.empty_display_type = 'CUBE'
            point.empty_display_size = 2

            arm = bpy.data.objects['%s' % mesh_name]
            arm.select_set(True)
            bpy.context.view_layer.objects.active = arm
            bpy.ops.object.mode_set(mode='EDIT')
            arm.data.edit_bones.active = arm.data.edit_bones[records[1]]

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            point.select_set(True)
            arm.select_set(True)
            bpy.context.view_layer.objects.active = arm
            bpy.ops.object.parent_set(type='BONE', keep_transform=False)
            print("setting parent")

            # point.parent = root_obj
            # point.parent_type = "BONE"
            # print(root_obj.pose.bones.keys())
            # rig.pose.bones[records[1]]
            # bone = rig.pose.bones[]
            # point.parent_bone = records[1]
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')  # deselect all objects


def string_to_vector(line: str) -> Vector:
    lines = line.split(",")
    print(lines)
    return Vector((float(lines[0]), float(lines[1]), float(lines[2])))


def string_to_quaternion(line: str) -> Quaternion:
    lines = line.split(",")
    return Quaternion((float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3])))
