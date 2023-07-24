import bpy
import bmesh
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty


def register():
    bpy.utils.register_class(MaterialEditQuail)


def unregister():
    bpy.utils.unregister_class(MaterialEditQuail)


def on_shader_change(self, context: bpy.types.Context):
    # get current material
    material = context.object.active_material  # type: ignore
    if material is None:
        return
    # set the fx custom property to the selected shader
    material["fx"] = self.shaders


class MaterialEditQuail(bpy.types.Panel):
    bl_idname = "QUAIL_PT_panel"
    bl_label = "EverQuest"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        row = layout.row()
        layout.prop(context.scene.quail_props, "shaders")
        layout.separator()
