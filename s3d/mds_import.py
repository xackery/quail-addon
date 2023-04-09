import bpy
import os
from ..common.material import add_material, add_material_property
from mathutils import Vector, Quaternion


def mds_import(root_path, path, is_visible) -> bool:
    ext = os.path.splitext(path)[1]
    if ext != ".mds":
        return False

    print("importing mds", path)
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
                    add_material(records[0], records[1], records[2])
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
                if records[1] == "e_TextureDiffuse0" and records[2][-4:] == ".dds" and os.path.exists(root_path+"/"+records[2][:-4]+".txt"):
                    with open(root_path+"/"+records[2][:-4]+".txt") as f:
                        anim_data = f.read()
                        material = bpy.data.materials[records[0]]
                        material["anim_data"] = anim_data
                        # iterate anim_data line by line
                        # skip first line
                        lines = anim_data.splitlines()
                        lines.pop(0)
                        lines.pop(0)
                        for line in lines:
                            if records[2] == line:
                                continue
                            if line[-4:] != ".dds":
                                continue
                            line = line[:-4]
                            print("analyzing anim data line "+line)

                            if bpy.data.materials.find(line) == -1:
                                print("adding anim material")
                                # add material
                                add_material(
                                    line, records[1], records[2])
                                add_material_property(
                                    root_path, line, records[1], line+".dds", records[3])

    vert_mesh = []
    uv_mesh = []
    if os.path.exists(path+"/vertex.txt"):
        with open(path+"/vertex.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                vert_line = records[1].split(",")
                vert_mesh.append((float(vert_line[1]), -float(
                    vert_line[0]), -float(vert_line[2])))
                uv_line = records[3].split(",")
                uv_mesh.append((float(uv_line[0]), float(uv_line[1])))
    # uv_mesh.reverse()

    material_mesh = []
    normal_mesh = []
    if os.path.exists(path+"/triangle.txt"):
        with open(path+"/triangle.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split("|")
                normal_line = records[0].split(",")
                normal_mesh.append((int(normal_line[1]), int(
                    normal_line[0]), int(normal_line[2])))
                material_mesh.append(
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

    mesh.from_pydata(vert_mesh, [], normal_mesh)
    uvlayer = mesh.uv_layers.new(name=base_name+"_uv")
    for vert in mesh.vertices:
        uvlayer.data[vert.index].uv = uv_mesh[vert.index]

    # populate mesh polygons
    mesh.update(calc_edges=True)
    # set normal material index
    for i in range(len(mesh.polygons)):
        mesh.polygons[i].material_index = material_mesh[i]

    obj = bpy.data.objects.new(base_name, mesh)
    collection.objects.link(obj)

    if not is_visible:
        bpy.context.view_layer.active_layer_collection.children[name].hide_viewport = True
    return True
