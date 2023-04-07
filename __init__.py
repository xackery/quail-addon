import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup, Scene
from bpy.utils import register_class, unregister_class
import sys
import tempfile
import subprocess
import os
import stat

bl_info = {
    "name": "Quail",
    "author": "xackery",
    "version" : (1, 0),
    "blender" : (3, 4, 0),
    "location" : "File > Export, File > Import",
    "category" : "Import-Export",
    "description" : "Helper for EverQuest Archives",
}


from bpy_extras.io_utils import (
    ExportHelper,
    axis_conversion,
)

def write_tmp_file(context, selection, up, forward, mods):
    #get tmp filepath and add the tmpfile
    obj_tmp = tempfile.gettempdir() + "/objtemp.obj"
    #write obj file
    global_scale = bpy.data.scenes[0].unit_settings.scale_length * 1000.0
    from mathutils import Matrix
    g_matrix = (
            Matrix.Scale(global_scale, 4) @
            axis_conversion(
                to_forward=forward,
                to_up=up,
            ).to_4x4()
        )
    from . import export_shape
    return export_shape.save(context, filepath=obj_tmp, use_selection=selection,
                        use_edges=True, use_mesh_modifiers=mods, global_matrix=g_matrix)

def export_data(context, filepath, level, selection, batch_mode, up, forward, mods):
    cmd = bpy.utils.user_resource('SCRIPTS') + "/addons/quail-plugin/quail"
    # add suffix based on platform
    if sys.platform == "win32":
        cmd += ".exe"
    if sys.platform == "linux":
        cmd += "-linux"
    if sys.platform == "darwin":
        cmd += "-darwin"

    mode = os.stat(cmd).st_mode
    if mode != 33261:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    obj_tmp = tempfile.gettempdir() + "/objtemp.obj"

    print("Writing temperory mesh file.. \n")
    write_tmp_file(context, selection, up, forward, mods)
    print("Converting data and saving as FLO...\n")
    process = subprocess.run([cmd, obj_tmp, filepath, level])
    if process.returncode == 0:
        print("Wrote FLO file", filepath)
    if os.path.exists(obj_tmp):
        os.remove(obj_tmp)
    return {'FINISHED'}

def import_data(context, filepath):
    cmd = bpy.utils.user_resource('SCRIPTS') + "/addons/quail-plugin/quail"
    # add suffix based on platform
    if sys.platform == "win32":
        cmd += ".exe"
    if sys.platform == "linux":
        cmd += "-linux"
    if sys.platform == "darwin":
        cmd += "-darwin"

    mode = os.stat(cmd).st_mode
    if mode != 33261:
        os.chmod(cmd, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # get base of filepath
    pfs_tmp = tempfile.gettempdir() + "/" + os.path.basename(filepath)
    print("pfs_tmp", pfs_tmp)

    print("Importing data...\n")
    #process = subprocess.run([cmd, obj_tmp, filepath, level])
    #if process.returncode == 0:
    #    print("Wrote FLO file", filepath)
    #if os.path.exists(obj_tmp):
    #    os.remove(obj_tmp)

    #path = "/Users/xackery/Documents/code/projects/quail/model/mesh/mod/test/_it13900.mod"
    path = "/Users/xackery/Documents/code/projects/quail/model/mesh/mds/test/_xhf.mds"

    name = os.path.basename(path)
    #trim prefix _ if it exists
    if name[0] == "_":
        name = name[1:]
    base_name = os.path.splitext(name)[0]

    mesh = bpy.data.meshes.new(base_name+"_mesh")
    # create a dictionary of materials
    materials = {}
    material_indexes = []
    material_shaders = {}

    if os.path.exists(path+"/material.txt"):
        with open(path+"/material.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split(" ")
                material = bpy.data.materials.new(name=records[0])
                # add material to dictionary
                materials[records[0]] = material
                material.use_nodes = True
                mesh.materials.append(material)
                material_indexes.append(records[0])
                material_shaders[records[0]] = "Opaque_MaxCB1.fx"
                print("adding material", records[0])

    if os.path.exists(path+"/material_property.txt"):
        with open(path+"/material_property.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split(" ")
                # get material from materials
                material = materials[records[0]]
                if records[1] == "e_TextureDiffuse0":
                    # create image
                    image = bpy.data.images.load(path+"/"+records[2])
                    # create texture
                    texture = bpy.data.textures.new(name=records[2], type='IMAGE')
                    texture.image = image
                    # create texture node
                    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
                    texture_node.image = image
                    # link nodes
                    material.node_tree.links.new(texture_node.outputs[0], material.node_tree.nodes["Principled BSDF"].inputs[0])
                    # set node position
                    texture_node.location = (-350, 280)
                if records[1] == "e_TextureNormal0":
                    # create image
                    image = bpy.data.images.load(path+"/"+records[2])
                    # create texture
                    texture = bpy.data.textures.new(name=records[2], type='IMAGE')
                    texture.image = image
                    # create texture node
                    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
                    texture_node.image = image
                    material.node_tree.links.new(texture_node.outputs[0], material.node_tree.nodes["Principled BSDF"].inputs[22])
                    # move node
                    texture_node.location = (-350, 0)


    for material_name in material_indexes:
        material = materials[material_name]
        if material_shaders[material_name] == "Opaque_MaxCB1.fx":
            # turn off metallic
            material.node_tree.nodes["Principled BSDF"].inputs[4].default_value = 0
            # turn off specular
            material.node_tree.nodes["Principled BSDF"].inputs[5].default_value = 0
            # turn off specular tint
            material.node_tree.nodes["Principled BSDF"].inputs[6].default_value = 0
            # turn off roughness
            material.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0
            # turn off anisotropic
            material.node_tree.nodes["Principled BSDF"].inputs[8].default_value = 0



    vert_mesh = []
    uv_mesh = []
    if os.path.exists(path+"/vertex.txt"):
        with open(path+"/vertex.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split(" ")
                vert_line = records[1].split(",")
                vert_mesh.append((float(vert_line[0]), float(vert_line[1]), float(vert_line[2])))
                uv_line = records[2].split(",")
                uv_mesh.append((float(uv_line[0]), float(uv_line[1])))

    material_mesh = []
    normal_mesh = []
    if os.path.exists(path+"/triangle.txt"):
        with open(path+"/triangle.txt") as f:
            lines = f.readlines()
            # skip first line
            lines.pop(0)
            for line in lines:
                records = line.split(" ")
                normal_line = records[0].split(",")
                normal_mesh.append((int(normal_line[0]), int(normal_line[1]), int(normal_line[2])))
                for i, material_name in enumerate(material_indexes):
                    if material_name == records[2]:
                        material_mesh.append(i)


    mesh.from_pydata(vert_mesh, [], normal_mesh)
    # populate mesh polygons
    mesh.update(calc_edges=True)
    # set normal material index
    mesh.polygons.foreach_set("material_index", material_mesh)

    uvlayer = mesh.uv_layers.new(name=base_name+"_uv")
    for vert in mesh.vertices:
        uvlayer.data[vert.index].uv = uv_mesh[vert.index]


    obj = bpy.data.objects.new(base_name, mesh)

    collection = bpy.data.collections.new(name)
    collection.objects.link(obj)
    # put collection in scene
    bpy.context.scene.collection.children.link(collection)

    return {'FINISHED'}

class ExportQuail(Operator, ExportHelper):
    bl_idname = "export_flo.subdiv_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export EQG"

    # ExportHelper mixin class uses this
    filename_ext = ".eqg"

    filter_glob: StringProperty(
        default="*.eqg|*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    is_apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply Modifiers",
        default=True,
    )

    def execute(self, context):
        return export_data(context,
                            self.filepath,
                            self.is_apply_modifiers)


class ImportQuail(Operator, ExportHelper):
    bl_idname = "import_flo.subdiv_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import EQG"

    # ImportHelper mixin class uses this
    filename_ext = ".eqg|.s3d"

    filter_glob: StringProperty(
        default="*.eqg|*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return import_data(context,
                            self.filepath)


def menu_func_export(self, context):
    self.layout.operator(ExportQuail.bl_idname, text="EverQuest Archive (.eqg/.s3d)")

def menu_func_import(self, context):
    self.layout.operator(ImportQuail.bl_idname, text="EverQuest Archive (.eqg/.s3d)")

def register():
    bpy.utils.register_class(ExportQuail)
    bpy.utils.register_class(ImportQuail)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportQuail)
    bpy.utils.unregister_class(ImportQuail)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()