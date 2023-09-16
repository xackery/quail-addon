# pyright: basic, reportOptionalMemberAccess=false, reportGeneralTypeIssues=false

import bpy
import os
from mathutils import Vector, Quaternion
import bmesh
from ..common import string_to_vector, string_to_quaternion

default_ani = ""


def ani_load(quail_path: str, ani_path: str):
    return
    ani_name = os.path.basename(ani_path)
    ani_name = os.path.splitext(ani_name)[0]  # take off .ani extension
    # get the last data after _

    prefix_name = ani_name
    suffix_name = ani_name
    names = ani_name.split("_")
    if len(names) > 1:
        prefix_name = names[0]
        suffix_name = names[len(names)-1]
    full_name = ani_name.lower()+"_rig"
    prefix_name = prefix_name.lower()+"_rig"
    suffix_name = suffix_name.lower()+"_rig"
    partial_name = '_'.join(names[0:len(names)-1]).lower()+"_rig"

    rig = bpy.data.objects.get(full_name)  # type: bpy.types.Armature
    if rig is None:
        rig = bpy.data.objects.get(prefix_name)
    if rig is None:
        rig = bpy.data.objects.get(suffix_name)
    if rig is None:
        rig = bpy.data.objects.get(partial_name)
    if rig is None:
        print("Rig %s, %s, %s, or %s from %s not found" %
              (full_name, prefix_name, partial_name, suffix_name, ani_name))
        return

    global default_ani
    if default_ani == "":
        default_ani = ani_name

    if ani_name.find("STND") != -1 or ani_name.find("default") != -1:
        default_ani = ani_name

    print("> Animation %s attaching to rig %s" % (ani_name, rig.name))
    r = open("%s/animation.txt" % ani_path, "r")
    lines = r.readlines()
    # skip first line
    lines.pop(0)
    is_strict = False
    for line in lines:
        records = line.split("|")
        if records[0] == "is_strict":
            is_strict = records[1] == "1"
            continue

    bpy.context.view_layer.objects.active = rig
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()

    action = bpy.data.actions.new(name=ani_name)
    action["is_strict"] = is_strict
    rig.animation_data_create()
    rig.animation_data.action = action

    for sub_path, dirs, files in os.walk(ani_path):
        for file in files:
            sub_ext = os.path.splitext(file)[1]
            if sub_ext != ".txt":
                continue
            if file == "animation.txt":
                continue
            with open("%s/%s" % (ani_path, file), "r") as fr:
                lines = fr.readlines()
                bone_name = os.path.basename(file)
                bone_name = os.path.splitext(bone_name)[0]

                # type: bpy.types.PoseBone
                bone = rig.pose.bones.get(bone_name)
                if bone is None:
                    print("Bone %s not found" % bone_name)
                    return
                bone.rotation_mode = 'QUATERNION'
                bone.keyframe_insert(
                    data_path="rotation_quaternion", frame=0)

                # skip first line
                lines.pop(0)
                for line in lines:
                    records = line.split("|")
                    milliseconds = int(records[0])
                    rotation = string_to_quaternion(records[1])
                    scale = string_to_vector(records[2])
                    translation = string_to_vector(records[3])

                    bone.rotation_quaternion = rotation
                    bone.scale = scale
                    bone.location = translation
                    bone.keyframe_insert(
                        data_path="rotation_quaternion", frame=milliseconds/10.0, index=-1, group=ani_name)
                    bone.keyframe_insert(
                        data_path="scale", frame=milliseconds/10.0, index=-1, group=ani_name)
                    bone.keyframe_insert(
                        data_path="location", frame=milliseconds/10.0, index=-1, group=ani_name)
    r.close()

    if rig.animation_data.action is None:
        rig.animation_data.action = bpy.data.actions.get(default_ani)
    if rig.animation_data.action.name != default_ani:
        rig.animation_data.action = bpy.data.actions.get(default_ani)
