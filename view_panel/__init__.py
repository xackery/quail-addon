# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import bmesh
from bpy_types import Operator
from ..exporter import export_data
from ..common import dialog
import os
addon_keymaps = []


def register():
    bpy.utils.register_class(ViewPanelQuail)
    bpy.utils.register_class(QUAIL_PT_fast_export)
    bpy.app.handlers.depsgraph_update_post.append(
        on_selection_changed)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(
            name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            QUAIL_PT_fast_export.bl_idname, type='E', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(ViewPanelQuail)
    bpy.utils.unregister_class(QUAIL_PT_fast_export)
    if on_selection_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(
            on_selection_changed)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


class ViewPanelQuail(bpy.types.Panel):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "QUAIL_PT_view"
    bl_label = "EverQuest"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'EverQuest'

    context_label: str = ""
    display_label: str = ""
    flag_label: str = ""
    view_mode: str = ""
    particle_rig_label: str = ""

    def draw(self, context: bpy.types.Context):

        if self.object_draw(context):
            return
        if self.mesh_draw(context):
            return
        if self.particle_draw(context):
            return
        if self.rig_draw(context):
            return

        layout = self.layout
        row = layout.row()
        if context.mode != "OBJECT":
            row.label(text=self.display_label)
            return
        row.label(text="Fast Export")
        layout.prop(context.scene.quail_props,
                    "fast_export_path", text="")
        layout.operator("quail.fast_export", icon='IMPORT', text="Export")

    def object_draw(self, context: bpy.types.Context) -> bool:
        if self.view_mode != "object":
            return False
        layout = self.layout
        row = layout.row()
        row.label(text="%s.%s" % (self.context_label,
                                  context.scene.quail_props.object_types))
        layout.prop(context.scene.quail_props, "object_types",
                    toggle=True)
        row = layout.row()
        row.label(text=self.display_label)
        self.flag_box_draw(context)
        return True

    def mesh_draw(self, context: bpy.types.Context) -> bool:
        if self.view_mode != "mesh":
            return False
        layout = self.layout
        row = layout.row()
        row.label(text="%s.%s" % (self.context_label,
                                  context.scene.quail_props.object_types))
        row = layout.row()
        layout.prop(context.scene.quail_props, "object_types",
                    toggle=True)
        row = layout.row()
        row.label(text=self.display_label)

        if context.scene.is_flags_open:
            self.flag_box_draw(context)
        return True

    def particle_draw(self, context: bpy.types.Context) -> bool:
        if self.view_mode != "particle":
            return False
        layout = self.layout
        row = layout.row()
        row.label(text="%s.%s" % (self.context_label,
                                  context.scene.quail_props.object_types))
        layout.prop(context.scene.quail_props, "object_types",
                    toggle=True)
        if self.display_label != "":
            row = layout.row()
            row.label(text=self.display_label)

        if self.particle_rig_label == "":
            return True

        row = layout.row()
        row.label(text="Rig: %s" % self.particle_rig_label)
        row = layout.row()
        row.prop(context.scene.quail_props, "bones")

        # row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

        # col = row.column(align=True)
        # col.operator("object.material_slot_add", icon='ADD', text="")
        # col.operator("object.material_slot_remove", icon='REMOVE', text="")

        # col.separator()

        return True

    def rig_draw(self, context: bpy.types.Context) -> bool:
        if self.view_mode != "rig":
            return False
        layout = self.layout
        row = layout.row()
        row.label(text="%s.%s" % (self.context_label,
                                  context.scene.quail_props.object_types))
        layout.prop(context.scene.quail_props, "object_types",
                    toggle=True)
        row = layout.row()
        row.label(text=self.display_label)

        return True

    def flag_box_draw(self, context: bpy.types.Context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        col = box.column()
        row.prop(context.scene, "is_flags_open", text="", emboss=False,
                 icon="TRIA_DOWN" if context.scene.is_flags_open else "TRIA_RIGHT", icon_only=True, toggle=True)
        row.label(text=self.flag_label)
        if not context.scene.is_flags_open:
            return

        sel_count = len(context.selected_objects)
        if sel_count != 1:
            return

        props = bpy.data.scenes.get("Scene").quail_props
        col.prop(context.scene.quail_props, "flag_no_collide",
                 toggle=True)
        col.prop(context.scene.quail_props,
                 "flag_is_invisible",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_three",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_four",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_five",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_six",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_seven",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_eight",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_nine",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_ten",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_eleven",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twelve",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_thirteen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_fourteen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_fifteen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_sixteen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_seventeen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_eighteen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_nineteen",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twenty",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentyone",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentytwo",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentythree",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentyfour",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentyfive",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentysix",
                 toggle=True)


class QUAIL_PT_fast_export(Operator):
    bl_idname = "quail.fast_export"
    bl_label = "Fast Export"
    bl_description = "Export the selected object to a eqg/s3d file"
    bl_options = {'REGISTER'}

    def execute(self, context):
        path = context.scene.quail_props.fast_export_path
        if path == "":
            dialog.message_box("Please set a path in the export panel",
                               "Error", 'ERROR')
            return {'CANCELLED'}
        if not path.endswith(".eqg") and not path.endswith(".s3d"):
            dialog.message_box("Please set a path with a .eqg or .s3d extension",
                               "Error", 'ERROR')
            return {'CANCELLED'}

        if bpy.data.filepath == "":
            dialog.message_box("Please save the blend file first",
                               "Error", 'ERROR')
            return {'CANCELLED'}
        base_path = os.path.dirname(bpy.data.filepath)
        path = os.path.join(base_path, path)

        if export_data(context, path, False):
            dialog.message_box("Exported to %s" % path,
                               "Success", 'INFO')
            return {'FINISHED'}
        return {'CANCELLED'}


def on_selection_changed(scene):
    bpy.types.QUAIL_PT_view.context_label = ""
    bpy.types.QUAIL_PT_view.view_mode = "none"
    on_mesh_select(scene)
    on_particle_select(scene)
    on_face_select(scene)
    on_rig_select(scene)


def on_mesh_select(scene):
    if bpy.context.mode != 'OBJECT':
        return
    obj = bpy.context.object
    if obj == None:
        return
    on_model_select(scene)

    view = bpy.types.QUAIL_PT_view
    view.flag_label = "Flags: 0"
    view.display_label = ""
    sel_count = len(bpy.context.selected_objects)
    if sel_count != 1:
        if sel_count > 1:
            view.display_label = "Too many objects selected"
        else:
            view.display_label = "Select an object to edit details"
        return

    bpy.types.QUAIL_PT_view.view_mode = "object"

    if obj.type == "EMPTY":
        if obj.empty_display_type == "PLAIN_AXES":
            ext = obj.get('ext')
            if ext is None:
                ext = "pts"
            bpy.types.QUAIL_PT_view.view_mode = "particle"
            return

    if obj.type != "MESH":
        view.display_label = "Select a mesh object to edit details"
        return


def on_particle_select(scene):
    if bpy.context.mode != 'OBJECT':
        return
    obj = bpy.context.object
    if obj == None:
        return
    on_model_select(scene)

    if obj.type != "EMPTY":
        return

    if obj.empty_display_type != "PLAIN_AXES":
        return

    bpy.types.QUAIL_PT_view.view_mode = "particle"
    view = bpy.types.QUAIL_PT_view

    if len(obj.users_collection) == 0:
        view.display_label = "Particle must be part of collection"
        return

    if obj.users_collection[0].name == "Scene Collection":
        view.display_label = "Particle must be part of collection"
        return

    for obj in obj.users_collection[0].objects:
        if obj.type != "ARMATURE":
            continue
        view.particle_rig_label = obj.name


def on_rig_select(scene):
    if bpy.context.mode != 'OBJECT':
        return
    obj = bpy.context.object
    if obj == None:
        return
    if obj.type != "ARMATURE":
        return

    on_model_select(scene)
    view = bpy.types.QUAIL_PT_view
    view.view_mode = "rig"


def on_model_select(scene):
    obj = bpy.context.object
    if obj == None:
        return
    view = bpy.types.QUAIL_PT_view
    ext = ""
    if len(obj.users_collection) == 0:
        ext = obj.get('ext')
        bpy.context.scene.quail_props.object_types = ext if ext != None else "mod"
        view.context_label = "Model: %s" % (obj.name)
        return

    if obj.users_collection[0].name == "Scene Collection":
        ext = obj.get('ext')
        bpy.context.scene.quail_props.object_types = ext if ext != None else "mod"
        view.context_label = "Model: %s" % (obj.name)
        return

    ext = obj.users_collection[0].get('ext')
    bpy.context.scene.quail_props.object_types = ext if ext != None else "mod"
    view.context_label = "Model: %s" % (
        obj.users_collection[0].name)


def on_face_select(scene):
    on_model_select(scene)
    active_object = bpy.context.active_object
    context = bpy.context
    if active_object == None:
        return

    if active_object.type != 'MESH':
        return

    if context.mode != 'EDIT_MESH':
        return

    view = bpy.types.QUAIL_PT_view

    if context.tool_settings.mesh_select_mode[2] != True:
        view.display_label = "Use face select to edit details"
        return

    sel_count = len(context.selected_objects)
    if sel_count != 1:
        if sel_count > 1:
            view.display_label = "Too many faces selected"
        else:
            view.display_label = "Select a face to edit details"
        return

    bpy.types.QUAIL_PT_view.view_mode = "mesh"

    bm = bmesh.from_edit_mesh(context.object.data)
    flag_layer = bm.faces.layers.float.get("flag")
    if flag_layer is None:
        flag_layer = bm.faces.layers.float.new("flag")

    polygon = None
    for poly in bm.faces:
        if not poly.select:
            continue
        if polygon:
            view.display_label = "Too many faces selected"
            return
        polygon = poly

    if polygon == None:
        view.display_label = "Select a face to edit details"
        return

    view.display_label = "Face: %d" % polygon.index

    if polygon == None:
        return
    flags = int(polygon[flag_layer])

    if context.object.active_material is None:
        view.display_label = "Face (No Material %d)" % flags
    else:
        view.display_label = "Face (%s)" % (
            context.object.active_material.name)
    view.flag_label = "Flags: %d" % flags
    props = bpy.data.scenes[0].quail_props
    props.flag_no_collide = flags & 1 == 1
    props.flag_is_invisible = flags & 2 == 2
    props.is_three = flags & 8 == 8
    props.is_four = flags & 16 == 16
    props.is_five = flags & 32 == 32
    props.is_six = flags & 64 == 64
    props.is_seven = flags & 128 == 128
    props.is_eight = flags & 256 == 256
    props.is_nine = flags & 512 == 512
    props.is_ten = flags & 1024 == 1024
    props.is_eleven = flags & 2048 == 2048
    props.is_twelve = flags & 4096 == 4096
    props.is_thirteen = flags & 8192 == 8192
    props.is_fourteen = flags & 16384 == 16384
    props.is_fifteen = flags & 32768 == 32768
    props.is_sixteen = flags & 65536 == 65536
    props.is_seventeen = flags & 131072 == 131072
    props.is_eighteen = flags & 262144 == 262144
    props.is_nineteen = flags & 524288 == 524288
    props.is_twenty = flags & 1048576 == 1048576
    props.is_twentyone = flags & 2097152 == 2097152
    props.is_twentytwo = flags & 4194304 == 4194304
    props.is_twentythree = flags & 8388608 == 8388608
    props.is_twentyfour = flags & 16777216 == 16777216
    props.is_twentyfive = flags & 33554432 == 33554432
    props.is_twentysix = flags & 67108864 == 67108864


def bone_list_update(self, context: bpy.types.Context):
    bones = [("ATTACH_TO_ORIGIN", "ATTACH_TO_ORIGIN",
              "Center on 0,0,0 of the model")]
    view = bpy.types.QUAIL_PT_view
    if view.particle_rig_label == "":
        return bones
    obj = context.scene.objects.get(view.particle_rig_label)
    if obj == None:
        return bones
    if obj.type != "ARMATURE":
        return bones

    # iterate bones
    for bone in obj.data.bones:
        bones.append((bone.name, bone.name, "Attach to %s" % bone.name))
    return bones


def on_ext_change(self, context: bpy.types.Context):
    obj = bpy.context.object
    if len(obj.users_collection) > 0 and obj.users_collection[0].name != "Scene Collection":
        if obj.users_collection[0].get('ext') == context.scene.quail_props.object_types:
            return
        obj.users_collection[0]['ext'] = context.scene.quail_props.object_types
        return
    if obj.get('ext') == context.scene.quail_props.object_types:
        return
    obj['ext'] = context.scene.quail_props.object_types


def on_flag_change(self, context: bpy.types.Context):
    props = bpy.data.scenes[0].quail_props
    flags = 0

    if props.flag_no_collide:
        flags |= 1 << 1
    if props.flag_is_invisible:
        flags |= 1 << 2
    if props.is_three:
        flags |= 1 << 3
    if props.is_four:
        flags |= 1 << 4
    if props.is_five:
        flags |= 1 << 5
    if props.is_six:
        flags |= 1 << 6
    if props.is_seven:
        flags |= 1 << 7
    if props.is_eight:
        flags |= 1 << 8
    if props.is_nine:
        flags |= 1 << 9
    if props.is_ten:
        flags |= 1 << 10
    if props.is_eleven:
        flags |= 1 << 11
    if props.is_twelve:
        flags |= 1 << 12
    if props.is_thirteen:
        flags |= 1 << 13
    if props.is_fourteen:
        flags |= 1 << 14
    if props.is_fifteen:
        flags |= 1 << 15
    if props.is_sixteen:
        flags |= 1 << 16
    if props.is_seventeen:
        flags |= 1 << 17
    if props.is_eighteen:
        flags |= 1 << 18
    if props.is_nineteen:
        flags |= 1 << 19
    if props.is_twenty:
        flags |= 1 << 20
    if props.is_twentyone:
        flags |= 1 << 21
    if props.is_twentytwo:
        flags |= 1 << 22
    if props.is_twentythree:
        flags |= 1 << 23
    if props.is_twentyfour:
        flags |= 1 << 24
    if props.is_twentyfive:
        flags |= 1 << 25
    if props.is_twentysix:
        flags |= 1 << 26

    active_object = bpy.context.active_object
    context = bpy.context
    if active_object == None:
        return

    if active_object.type != 'MESH':
        return

    if context.mode != 'EDIT_MESH':
        return

    if context.tool_settings.mesh_select_mode[2] != True:
        return

    sel_count = len(context.selected_objects)
    if sel_count != 1:
        return

    bm = bmesh.from_edit_mesh(context.object.data)
    flag_layer = bm.faces.layers.float.get("flag")
    if flag_layer is None:
        flag_layer = bm.faces.layers.float.new("flag")

    polygon = None
    for poly in bm.faces:
        if not poly.select:
            continue
        if polygon:
            return
        polygon = poly

    if polygon == None:
        return
    polygon[flag_layer] = flags
    bmesh.update_edit_mesh(context.object.data)
