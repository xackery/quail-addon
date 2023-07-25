import bpy
import bmesh


def on_selection_changed(scene):
    bpy.types.QUAIL_PT_view.context_label = ""  # type: ignore
    on_mesh_select(scene)
    on_face_select(scene)


def on_mesh_select(scene):
    if bpy.context.mode != 'OBJECT':
        return

    view = bpy.types.QUAIL_PT_view  # type: ignore
    view.flag_label = "Flags: 0"
    view.display_label = ""
    sel_count = len(bpy.context.selected_objects)
    if sel_count != 1:
        if sel_count > 1:
            view.display_label = "Too many objects selected"
        else:
            view.display_label = "Select an object to edit details"
        return

    obj = bpy.context.object
    if obj.type != "MESH":
        view.display_label = "Select a mesh object to edit details"
        return
    if len(obj.users_collection) > 0 and obj.users_collection[0].name != "Scene Collection":
        # type: ignore
        ext = obj.users_collection[0].get(
            'ext')
        if ext is None:
            ext = "mod"
        bpy.context.scene.quail_props.object_types = ext
        view.context_label = "Model: %s" % obj.users_collection[0].name
        return
    ext = obj.get('ext')  # type: ignore
    if ext is None:
        ext = "mod"
    bpy.context.scene.quail_props.object_types = ext
    view.context_label = "Model: %s" % obj.name


def on_face_select(scene):
    active_object = bpy.context.active_object
    context = bpy.context
    if active_object == None:
        return

    if active_object.type != 'MESH':
        return

    if context.mode != 'EDIT_MESH':
        return

    view = bpy.types.QUAIL_PT_view  # type: ignore

    if context.tool_settings.mesh_select_mode[2] != True:
        view.display_label = "Use face select to edit details"
        return

    sel_count = len(context.selected_objects)
    if sel_count != 1:
        if sel_count > 1:
            view.display_label = "Too many faces selected"
        else:
            view.display_label = "Select a face to edit details"  # type: ignore
        return

    bm = bmesh.from_edit_mesh(context.object.data)  # type: ignore
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    polygon = None
    for poly in bm.faces:  # type: ignore
        if not poly.select:
            continue
        if polygon:
            view.display_label = "Too many faces selected"
            return
        polygon = poly

    if polygon == None:
        view.display_label = "Select a face to edit details"
        return

    obj = bpy.context.object
    if len(obj.users_collection) > 0 and obj.users_collection[0].name != "Scene Collection":
        bpy.context.scene.quail_props.object_types = obj.users_collection[0].get(
            'ext')
        view.context_label = "Model: %s" % obj.users_collection[0].name
    else:
        bpy.context.scene.quail_props.object_types = obj.get(
            'ext')  # type: ignore
        view.context_label = "Model: %s" % (active_object.name)
    view.display_label = "Face: %d" % polygon.index

    if polygon == None:
        return
    flags = polygon[flag_layer]

    if context.object.active_material is None:
        view.display_label = "Face (No Material %d)" % flags
    else:
        view.display_label = "Face (%s)" % (
            context.object.active_material.name)
    view.flag_label = "Flags: %d" % flags
    props = bpy.data.scenes[0].quail_props  # type: ignore
    props.flag_no_collide = flags & 1 == 1  # type: ignore
    props.flag_is_invisible = flags & 2 == 2  # type: ignore
    props.is_three = flags & 8 == 8  # type: ignore
    props.is_four = flags & 16 == 16  # type: ignore
    props.is_five = flags & 32 == 32  # type: ignore
    props.is_six = flags & 64 == 64  # type: ignore
    props.is_seven = flags & 128 == 128  # type: ignore
    props.is_eight = flags & 256 == 256  # type: ignore
    props.is_nine = flags & 512 == 512  # type: ignore
    props.is_ten = flags & 1024 == 1024  # type: ignore
    props.is_eleven = flags & 2048 == 2048  # type: ignore
    props.is_twelve = flags & 4096 == 4096  # type: ignore
    props.is_thirteen = flags & 8192 == 8192  # type: ignore
    props.is_fourteen = flags & 16384 == 16384  # type: ignore
    props.is_fifteen = flags & 32768 == 32768  # type: ignore
    props.is_sixteen = flags & 65536 == 65536  # type: ignore
    props.is_seventeen = flags & 131072 == 131072  # type: ignore
    props.is_eighteen = flags & 262144 == 262144  # type: ignore
    props.is_nineteen = flags & 524288 == 524288  # type: ignore
    props.is_twenty = flags & 1048576 == 1048576  # type: ignore
    props.is_twentyone = flags & 2097152 == 2097152  # type: ignore
    props.is_twentytwo = flags & 4194304 == 4194304  # type: ignore
    props.is_twentythree = flags & 8388608 == 8388608  # type: ignore
    props.is_twentyfour = flags & 16777216 == 16777216  # type: ignore
    props.is_twentyfive = flags & 33554432 == 33554432  # type: ignore
    props.is_twentysix = flags & 67108864 == 67108864  # type: ignore


def register():
    bpy.utils.register_class(ViewPanelQuail)
    bpy.app.handlers.depsgraph_update_post.append(
        on_selection_changed)  # type: ignore


def unregister():
    bpy.utils.unregister_class(ViewPanelQuail)
    bpy.app.handlers.depsgraph_update_post.remove(
        on_selection_changed)  # type: ignore


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

    flag_cache: int = 0
    object_id_cache: int = -1
    face_id_cache: int = -1

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        row = layout.row()
        if self.context_label == "":
            row.label(text="Select an object to edit details")
            return
        else:
            row.label(text="%s.%s" % (self.context_label,
                                      context.scene.quail_props.object_types))  # type: ignore
            layout.prop(context.scene.quail_props, "object_types",  # type: ignore
                        toggle=True)
        row = layout.row()
        row.label(text=self.display_label)
        self.object_draw(context)
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "is_flags_open", text="", emboss=False,
                 icon="TRIA_DOWN" if context.scene.is_flags_open else "TRIA_RIGHT", icon_only=True, toggle=True)
        row.label(text=self.flag_label)

        if context.scene.is_flags_open:
            self.flag_draw(box, context)

    def object_draw(self, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return
        return

    def flag_draw(self, box: bpy.types.UILayout, context: bpy.types.Context):
        if context.mode != 'EDIT_MESH':
            return
        layout = self.layout
        sel_count = len(context.selected_objects)
        if sel_count != 1:
            return
        col = box.column()

        props = bpy.data.scenes.get("Scene").quail_props  # type: ignore
        col.prop(context.scene.quail_props, "flag_no_collide",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props,  # type: ignore
                 "flag_is_invisible",
                 toggle=True)
        col.prop(context.scene.quail_props, "is_three",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_four",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_five",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_six",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_seven",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_eight",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_nine",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_ten",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_eleven",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twelve",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_thirteen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_fourteen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_fifteen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_sixteen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_seventeen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_eighteen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_nineteen",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twenty",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentyone",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentytwo",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentythree",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentyfour",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentyfive",  # type: ignore
                 toggle=True)
        col.prop(context.scene.quail_props, "is_twentysix",  # type: ignore
                 toggle=True)


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
    props = bpy.data.scenes[0].quail_props  # type: ignore
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

    bm = bmesh.from_edit_mesh(context.object.data)  # type: ignore
    flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
    if flag_layer is None:
        flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

    polygon = None
    for poly in bm.faces:  # type: ignore
        if not poly.select:
            continue
        if polygon:
            return
        polygon = poly

    if polygon == None:
        return
    polygon[flag_layer] = flags
    bmesh.update_edit_mesh(context.object.data)  # type: ignore
