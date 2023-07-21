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

        # type: bmesh.types.BMesh
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
            text_label = "Face (%s)" % (context.object.active_material.name)
        row.label(text=text_label)
        layout.separator()
        col.prop(context.scene.quail_props, "flag_no_collide")  # type: ignore
        col.prop(context.scene.quail_props,  # type: ignore
                 "flag_is_invisible")


def on_collide_change(self, context: bpy.types.Context):
    print("collide changed to " + str(self.flag_no_collide))  # type: ignore
