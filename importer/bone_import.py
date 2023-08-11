# pyright: basic, reportOptionalMemberAccess=false, reportGeneralTypeIssues=false

import bpy
from ..common import string_to_vector, string_to_quaternion
from mathutils import Vector, Quaternion


def bone_parse(quail_path, mesh_path, mesh_name, is_visible, collection) -> bpy.types.Object:
    cur_path = "%s/bone.txt" % mesh_path

    print(">> Bone", mesh_name)
    arm = bpy.data.armatures.new(name=mesh_name+"_armature")
    # bpy.context.scene.collection.objects.link(arm)
    rig_name = mesh_name.lower()+"_rig"
    rig_obj = bpy.data.objects.new(rig_name, arm)
    collection.objects.link(rig_obj)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.editmode_toggle()

    bone_sel = bpy.data.objects.new(name="root", object_data=arm)

    bones = bone_load(cur_path)

    # collection.objects.link(bone_sel)

    if not bones:
        return rig_obj

    bpy.ops.object.mode_set(mode='EDIT')
    for i, bone in enumerate(bones):
        print(">>> %s" % bone['name'])

        bone_sel = arm.edit_bones.new(name=bone['name'])
        bone['ref'] = bone_sel
        if i == 0:
            bone_sel.head = (0, 0, 0)
            bone_sel.tail = bone['pivot']
            # rotation_matrix = bone['rotation'].to_matrix().to_4x4()
            # bone_sel.tail = bone_sel.head + \
            #     bone['pivot']+(rotation_matrix @ Vector((0, 1, 0)))

    bone_traverse(bones, bones[0])
    bpy.ops.object.mode_set(mode='OBJECT')

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
    #     bone_sel.parent = root_obj
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
    return rig_obj


def bone_traverse(bones: list, bone: dict):

    bone_cur = bone
    bone_cur_obj = bone_cur['ref']  # type: bpy.types.EditBone

    # rotation_matrix = bone_cur['rotation'].to_matrix().to_4x4()
    # bone_cur_obj.transform(rotation_matrix)
    # rotation_matrix = bone_cur['rotation'].to_matrix().to_4x4()
    # euler_rotation = bone_cur['rotation'].to_euler()
    # bone_cur_obj.tail = bone_cur_obj.tail + \
    #    (rotation_matrix @ Vector((0, 1, 0)))
    # bone_cur_obj.roll = euler_rotation.z
    if bone['children_count'] > 0:
        bone_sel = bones[bone['child_index']]
        if bone_sel is None:
            print(">> Bone %s child %d not found" %
                  (bone['name'], bone['next']))
            return
        bone_sel_obj = bone_sel['ref']  # type: bpy.types.EditBone
        bone_sel_obj.parent = bone_cur_obj
        bone_sel_obj.head = bone_cur_obj.tail
        bone_sel_obj.tail = bone_sel_obj.head+bone_sel['pivot']
        # rotation_matrix = bone_sel['rotation'].to_matrix().to_4x4()
        # bone_sel_obj.tail = bone_sel_obj.head + \
        #     bone_sel['pivot']+(rotation_matrix @ Vector((0, 1, 0)))

        bone_traverse(bones, bones[bone['child_index']])
    if bone['next'] > -1:
        bone_sel = bones[bone['next']]
        if bone_sel is None:
            print(">> Bone %s next %d not found" %
                  (bone['name'], bone['next']))
            return
        bone_sel_obj = bone_sel['ref']  # type: bpy.types.EditBone
        bone_sel['ref'].parent = bone_cur_obj.parent
        bone_sel_obj.head = bone_cur_obj.parent.tail
        bone_sel_obj.tail = bone_sel_obj.head+bone_sel['pivot']
        # rotation_matrix = bone_sel['rotation'].to_matrix().to_4x4()
        # bone_sel_obj.tail = bone_sel_obj.head + \
        #     bone_sel['pivot']+(rotation_matrix @ Vector((0, 1, 0)))
        # bone_sel_obj.tail = bone_sel['pivot']
        bone_traverse(bones, bones[bone['next']])

        # bone_sel['ref'].translate(bone_sel['pivot'])


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

            # z = bone["pivot"].y
            # bone["pivot"].y = bone["pivot"].z
            # bone["pivot"].z = z

            # x = bone["pivot"].x
            # bone["pivot"].x = bone["pivot"].y
            # bone["pivot"].y = -x
            bones.append(bone)
    return bones
