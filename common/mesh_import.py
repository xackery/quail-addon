import bpy
import os
from mathutils import Vector, Quaternion
from .loader import load_material, load_material_property


def mesh_import(root_path, path, is_visible) -> bool:
    if not os.path.exists(path+"/mesh.txt"):
        print("no mesh.txt, skip mesh_import")
        return False

    name = os.path.basename(path)
    if name[0] == "_":
        name = name[1:]
    print("importing meshes inside", name)

    collection = bpy.data.collections.new(name)
    # put collection in scene
    bpy.context.scene.collection.children.link(collection)

    mesh_names = []
    with open(path+"/mesh.txt") as f:
        mesh_names = f.readlines()
        # skip first line
        mesh_names.pop(0)
        for mesh_name in mesh_names:
            obj = mesh_parse(root_path, path, mesh_name.rstrip(), is_visible)
            collection.objects.link(obj)

    if not is_visible:
        bpy.context.view_layer.active_layer_collection.children[name].hide_viewport = True
    return True


def mesh_parse(root_path, path, name, is_visible) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name+"_mesh")
    print("> importing mesh", name)
    load_material(path, mesh)
    load_material_property(root_path, path, mesh)
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
                print(uv_line)
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

    # if os.path.exists(path+"/bone.txt"):
    #     arm = bpy.data.armatures.new(name="root")
    #     rig = bpy.data.objects.new("root", arm)
    #     bpy.context.scene.collection.objects.link(rig)
    #     bpy.context.view_layer.objects.active = rig
    #     bpy.ops.object.editmode_toggle()

    #     bone_obj = bpy.data.objects.new(
    #         name="root", object_data=arm)

    #     collection.objects.link(bone_obj)

    #     with open(path+"/bone.txt") as f:
    #         lines = f.readlines()
    #         # skip first line
    #         lines.pop(0)
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

    mesh.from_pydata(mesh_verts, [], mesh_normals)
    mesh.update(calc_edges=True)

    uvlayer = mesh.uv_layers.new(name=name+"_uv")
    print(len(mesh.vertices), len(mesh_uvs))
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
            uvlayer.data[triangle.loop_indices[i]].uv = mesh_uvs[vertex]
            i += 1

        # populate mesh polygons
        # set normal material index
    for i in range(len(mesh.polygons)):
        mesh.polygons[i].material_index = mesh_materials[i]
        # mesh.polygons[i]["flags"] = mesh_flags[i]
    obj = bpy.data.objects.new(name, mesh)
    return obj
