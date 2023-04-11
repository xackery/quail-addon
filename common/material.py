import bpy
import os


def add_material(material_name, flags, shader):
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material["flags"] = flags
    material["fx"] = shader
    if shader == "Opaque_MaxCB1.fx":
        pass
    # set specular to 0
    material.specular_intensity = 0
    return material


def add_material_property(root_path, material_name, property_name, property_value, property_category):
    material = bpy.data.materials[material_name]

    node_position = (0, 0)
    bsdf_index = -1

    if property_name == "e_TextureDiffuse0":
        bsdf_index = 0
        node_position = (-350, 280)
    elif property_name == "e_TextureNormal0":
        bsdf_index = 22
        node_position = (-350, 0)
    elif property_name == "e_fShininess0":
        material.node_tree.nodes["Principled BSDF"].inputs[7].default_value = float(
            property_value)
    if bsdf_index == -1:
        return

    # get node connected to diffuse
    for node in material.node_tree.nodes:
        if node.label == property_name:
            return

    texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture_node.label = property_name

    texture_path = os.path.join(root_path, property_value).lower()
    if not os.path.exists(texture_path):
        return

    image = bpy.data.images.load(texture_path)
    texture_node.image = image  # type: ignore

    material.node_tree.links.new(
        texture_node.outputs[0], material.node_tree.nodes["Principled BSDF"].inputs[bsdf_index])

    texture_node.location = node_position
