import bpy
import os
from mathutils import Vector, Quaternion
from .material import material_load, material_property_load


def mesh_import(root_path, path, is_visible) -> bool:
    if not os.path.exists(path+"/mesh.txt"):
        return False

    name = os.path.basename(path)
    if name[0] == "_":
        name = name[1:]
    print("Importing meshes from", name)

    collection = bpy.data.collections.new(name)
    # put collection in scene
    bpy.context.scene.collection.children.link(collection)

    mesh_names = []
    with open(path+"/mesh.txt") as f:
        mesh_names = f.readlines()
        # skip first line
        mesh_names.pop(0)
        for mesh_name in mesh_names:
            obj = mesh_parse(root_path, path,
                             mesh_name.rstrip(), is_visible)
            collection.objects.link(obj)

    if not is_visible:
        bpy.context.view_layer.active_layer_collection.children[name].hide_viewport = True
    return True


def mesh_parse(root_path, path, name, is_visible) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name+"_mesh")
    print("> Mesh", name)
    material_load(path, mesh)
    material_property_load(root_path, path, mesh)
    mesh_verts = []
    mesh_uvs = []
    cur_path = "%s/%s_vertex.txt" % (path, name)
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
    cur_path = "%s/%s_triangle.txt" % (path, name)
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
                mesh_materials.append(
                    bpy.data.materials.find(records[2].rstrip()))

    mesh.from_pydata(mesh_verts, [], mesh_normals)
    mesh.update(calc_edges=True)

    uvlayer = mesh.uv_layers.new(name=name+"_uv")
    # for vert in mesh.vertices:
    # print(vert.co, vert.index, mesh_uvs[vert.index])
    # uvlayer.data[vert.index].uv = mesh_uvs[vert.index]

    # for face in mesh.polygons:
    #    for vert_index, loop_index in zip(face.vertices, face.loop_indices):
    #        uvlayer.data[loop_index] = mesh_uvs[vert_index]

    for triangle in mesh.polygons:
        vertices = list(triangle.vertices)
        i = 0
        for vertex in vertices:
            uvlayer.data[triangle.loop_indices[i]
                         ].uv = mesh_uvs[vertex]
            i += 1

    # populate mesh polygons
    # set normal material index
    for i in range(len(mesh.polygons)):
        poly = mesh.polygons[i]
        poly.material_index = mesh_materials[i]
        # new_map = "flag_%d" % mesh_flags[i]
        # if new_map not in mesh.face_maps:
        #    mesh.face_maps.new(name=new_map)
        # face_map = mesh.face_maps[new_map]
        # bpy.ops.object.face_map_assign()

        # face_map.data. [poly.index].select = True

    faces = {}
    obj = bpy.data.objects.new(name, mesh)
    for i in range(len(mesh.polygons)):
        poly = mesh.polygons[i]
        poly.material_index = mesh_materials[i]
        new_map = "flag_%d" % mesh_flags[i]
        if new_map not in faces:
            faces[new_map] = []
        face_map = faces[new_map]
        face_map.append(i)

    for key in faces:
        if key not in obj.face_maps:
            face_map = obj.face_maps.new(name=key)
        face_map = obj.face_maps[key]
        face_map.add(faces[key])

    bone_parse(path, name, obj)
    return obj


def bone_parse(path, name, obj):
    cur_path = "%s/%s_bone.txt" % (path, name)
    if not os.path.exists(cur_path):
        return
    arm = bpy.data.armatures.new(name=name)
    rig = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.editmode_toggle()

    bone_obj = bpy.data.objects.new(name="root", object_data=arm)

    bones = []

    # collection.objects.link(bone_obj)

    with open(cur_path) as f:
        lines = f.readlines()
        lines.pop(0)
        for _, line in enumerate(lines):
            bones.append(line)

    if not bones:
        return

    bone_line = bones[0]
    bone_line = bone_line.split("|")
    # name|child_index|children_count|next|pivot|rotation|scale
    child_next_index = int(bone_line[1])
    children_count = int(bone_line[2])
    next_index = int(bone_line[3])
    position = bone_line[4].split(",")
    position = (float(position[0]), float(position[1]), float(position[2]))
    quad = bone_line[5].split(",")
    quad = (float(quad[0]), float(quad[1]), float(quad[2]), float(quad[3]))
    current_bone = arm.edit_bones.new(name=bone_line[0])
    current_bone.head = position

    if next_index == -1 and children_count > 0:
        bone_line = bones[child_next_index]
        bone_line = bone_line.split("|")
        child_next_index = int(bone_line[1])
        children_count = int(bone_line[2])
        next_index = int(bone_line[3])
        position = bone_line[4].split(",")
        position = (float(position[0]), float(position[1]), float(position[2]))
        quad = bone_line[5].split(",")
        quad = (float(quad[0]), float(quad[1]), float(quad[2]), float(quad[3]))
        current_bone.tail = position
        # quat_arm_space = Quaternion(quad)
        # current_bone.transform(quat_arm_space.to_matrix())
        # current_bone.translate(position)
        next_bone = arm.edit_bones.new(name=bone_line[0])
        next_bone.head = position
        next_bone.parent = current_bone
        current_bone = next_bone

        if next_index > 0:
            bone_line = bones[child_next_index]
            bone_line = bone_line.split("|")
            child_next_index = int(bone_line[1])
            children_count = int(bone_line[2])
            next_index = int(bone_line[3])
            next_bone = arm.edit_bones.new(name=bone_line[0])
            next_position = bone_line[4].split(",")
            next_position = (float(next_position[0]), float(
                next_position[1]), float(next_position[2]))
            next_quad = bone_line[5].split(",")
            next_quad = (float(next_quad[0]), float(quad[1]),
                         float(next_quad[2]), float(next_quad[3]))
            next_bone.head = (position[0]+next_position[0], position[1] +
                              next_position[1], position[2]+next_position[2])
            next_bone.parent = current_bone
    # parnt rig to obj with weighted contraints
    rig.parent = obj

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
