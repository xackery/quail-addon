import bpy
import os
from ..common.material import add_material, add_material_property
from mathutils import Vector, Quaternion


def mod_import(root_path, path, is_visible) -> bool:
    ext = os.path.splitext(path)[1]
    if ext != ".mod":
        return False

    print("importing mod", path)
    name = os.path.basename(path)

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
                if bpy.data.materials.get(records[0]) is None:
                    add_material(records[0].strip(),
                                 records[1].strip(), records[2].strip())
                mesh.materials.append(bpy.data.materials[records[0]])

    if os.path.exists(path+"/material_property.txt"):
        with open(path+"/material_property.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                add_material_property(
                    root_path, records[0], records[1], records[2], records[3])

    mesh_verts = []
    mesh_uvs = []
    if os.path.exists(path+"/vertex.txt"):
        with open(path+"/vertex.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                vert_line = records[1].split(",")
                mesh_verts.append((float(vert_line[0]), float(
                    vert_line[1]), float(vert_line[2])))
                uv_line = records[3].split(",")
                mesh_uvs.append((float(uv_line[0]), float(uv_line[1])))
    # uv_mesh.reverse()

    mesh_materials = []
    mesh_normals = []
    mesh_flags = []
    if os.path.exists(path+"/triangle.txt"):
        with open(path+"/triangle.txt") as f:
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

    collection = bpy.data.collections.new(name)
    # put collection in scene
    bpy.context.scene.collection.children.link(collection)

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
    uvlayer = mesh.uv_layers.new(name=base_name+"_uv")
    for vert in mesh.vertices:
        # print(vert.index, uv_mesh[vert.index])
        uvlayer.data[vert.index].uv = mesh_uvs[vert.index]

    # populate mesh polygons
    mesh.update(calc_edges=True)
    # set normal material index
    for i in range(len(mesh.polygons)):
        mesh.polygons[i].material_index = mesh_materials[i]
        # mesh.polygons[i]["flags"] = mesh_flags[i]

    obj = bpy.data.objects.new(base_name, mesh)
    collection.objects.link(obj)

    if not is_visible:
        bpy.context.view_layer.active_layer_collection.children[name].hide_viewport = True
    return True
