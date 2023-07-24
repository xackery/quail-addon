import bpy
import bmesh


def register():
    bpy.utils.register_class(ViewPanelQuail)


def unregister():
    bpy.utils.unregister_class(ViewPanelQuail)


class ViewPanelQuail(bpy.types.Panel):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "QUAIL_PT_view"
    bl_label = "EverQuest"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'EverQuest'

    flag_cache: int = 0
    object_id_cache: int = -1
    face_id_cache: int = -1

    def draw(self, context: bpy.types.Context):
        self.flag_render(context)
        self.object_render(context)

    def object_render(self, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return
        layout = self.layout
        row = layout.row()
        text_label = ""

        sel_count = len(context.selected_objects)
        if sel_count != 1:
            if sel_count > 1:
                text_label = "Too many objects selected"
            else:
                text_label = "Select an object to edit details"
            row.label(text=text_label)
            return

        obj = context.object
        if obj.type != "MESH":
            text_label = "Select a mesh object to edit details"
            row.label(text=text_label)
            return

        layout.prop(context.scene.quail_props, "object_types")  # type: ignore

    def flag_render(self, context: bpy.types.Context):
        if context.mode != 'EDIT_MESH':
            return
        layout = self.layout
        row = layout.row()
        text_label = ""

        if context.tool_settings.mesh_select_mode[2] != True:
            text_label = "Use face select to edit details"
            row.label(text=text_label)
            return

        sel_count = len(context.selected_objects)
        if sel_count != 1:
            if sel_count > 1:
                text_label = "Too many faces selected"
            else:
                text_label = "Select a face to edit details"
            row.label(text=text_label)
            return

        # if self.object_id_cache != context.object.data.id or self.face_id_cache != context.object.data.polygons.active.id:
        #     self.object_id_cache = context.object.data.id
        #     self.face_id_cache = context.object.data.polygons.active.id
        #     self.flag_cache = context.object.data.polygons.active[context.object.data.polygons.active.layers.int.get(
        #         "flag")]  # type: ignore

        # flags = self.flag_cache
        # # type: bmesh.types.BMesh
        bm = bmesh.from_edit_mesh(context.object.data)  # type: ignore
        # check if contains flags
        flag_layer = bm.faces.layers.int.get("flag")  # type: ignore
        if flag_layer is None:
            flag_layer = bm.faces.layers.int.new("flag")  # type: ignore

        polygon = None
        for poly in bm.faces:  # type: ignore
            if not poly.select:
                continue
            if polygon:
                text_label = "Too many faces selected"
                row.label(text=text_label)
                return
            polygon = poly

        if polygon == None:
            return
        flags = polygon[flag_layer]
        col = self.layout.column()

        if context.object.active_material is None:
            text_label = "Face (No Material)"
        else:
            text_label = "Face (%s %d)" % (
                context.object.active_material.name, flags)
        row.label(text=text_label)
        layout.separator()

        props = bpy.data.scenes.get("Scene").quail_props  # type: ignore
        col.prop(context.scene.quail_props, "flag_no_collide")  # type: ignore
        col.prop(context.scene.quail_props,  # type: ignore
                 "flag_is_invisible")
        col.prop(context.scene.quail_props, "is_three")  # type: ignore
        col.prop(context.scene.quail_props, "is_four")  # type: ignore
        col.prop(context.scene.quail_props, "is_five")  # type: ignore
        col.prop(context.scene.quail_props, "is_six")  # type: ignore
        col.prop(context.scene.quail_props, "is_seven")  # type: ignore
        col.prop(context.scene.quail_props, "is_eight")  # type: ignore
        col.prop(context.scene.quail_props, "is_nine")  # type: ignore
        col.prop(context.scene.quail_props, "is_ten")  # type: ignore
        col.prop(context.scene.quail_props, "is_eleven")  # type: ignore
        col.prop(context.scene.quail_props, "is_twelve")  # type: ignore
        col.prop(context.scene.quail_props, "is_thirteen")  # type: ignore
        col.prop(context.scene.quail_props, "is_fourteen")  # type: ignore
        col.prop(context.scene.quail_props, "is_fifteen")  # type: ignore
        col.prop(context.scene.quail_props, "is_sixteen")  # type: ignore


def on_flag_change(self, context: bpy.types.Context):
    print("collide is " + str(self.flag_no_collide))
    # props = bpy.data.scenes[0].quail_props  # type: ignore
    # flags = 1
    # props.flag_no_collide = flags & 1 == 1  # type: ignore
    # props.flag_is_invisible = flags & 2 == 2  # type: ignore
    # props.is_three = flags & 8 == 8  # type: ignore
    # props.is_four = flags & 16 == 16  # type: ignore
    # props.is_five = flags & 32 == 32  # type: ignore
    # props.is_six = flags & 64 == 64  # type: ignore
    # props.is_seven = flags & 128 == 128  # type: ignore
    # props.is_eight = flags & 256 == 256  # type: ignore
    # props.is_nine = flags & 512 == 512  # type: ignore
    # props.is_ten = flags & 1024 == 1024  # type: ignore
    # props.is_eleven = flags & 2048 == 2048  # type: ignore
    # props.is_twelve = flags & 4096 == 4096  # type: ignore
    # props.is_thirteen = flags & 8192 == 8192  # type: ignore
    # props.is_fourteen = flags & 16384 == 16384  # type: ignore
    # props.is_fifteen = flags & 32768 == 32768  # type: ignore
    # props.is_sixteen = flags & 65536 == 65536  # type: ignore
