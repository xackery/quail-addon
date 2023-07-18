import bpy
import os

materials = {}


def material_load(root_path: str, mesh_name: str, material_name: str) -> int:
    idx = material_find(material_name)
    if idx != -1:
        return idx
    return material_property_load(root_path, mesh_name, material_name)


def material_find(material_name: str) -> int:
    idx = bpy.data.materials.find(material_name)

    if idx != -1:
        return idx
    return bpy.data.materials.find(material_name.lower())


def material_property_load(root_path: str, mesh_name: str, material_name: str) -> int:
    property_path = root_path+"/"+mesh_name + \
        ".mesh/"+material_name+".material/property.txt"
    if not os.path.exists(property_path):
        print("property file not found: "+property_path)
        return -1

    idx = material_find(material_name)
    if idx == -1:
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
    else:
        material = bpy.data.materials[idx]

    with open(property_path) as f:
        lines = f.readlines()
        lines.pop(0)  # skip first line
        for line in lines:
            records = line.split("|")
            material_property_add(
                root_path, mesh_name, material_name, records[0], records[1], records[2])
            # if records[0] == "e_TextureDiffuse0" and records[1][-4:] == ".dds" and os.path.exists(root_path+"/"+records[1][:-4]+".txt"):
            #     with open(root_path+"/"+records[1][:-4]+".txt") as f:
            #         anim_data = f.read()
            #         material["anim_data"] = anim_data
            #         # iterate anim_data line by line
            #         # skip first line
            #         lines = anim_data.splitlines()
            #         lines.pop(0)
            #         for line in lines:
            #             if records[1] == line:
            #                 continue
            #             if line[-4:] != ".dds":
            #                 continue
            #             line = line[:-4]
            #             print("analyzing anim data line "+line)

            #             if bpy.data.materials.find(line) == -1:
            #                 print("adding anim material")
            #                 # add material
            #                 material_add(
            #                     line, material_name, records[1].strip())
            #                 material_property_add(
            #                     root_path, mesh_name, material_name.rstrip(), records[0], line.rstrip()+".dds", records[2].rstrip())
    return idx


def material_property_add(root_path: str, mesh_name: str, material_name: str, property_name: str, property_value: str, property_category: str):
    if material_name == "":
        print("material name is empty for material_property_add")
        return
    idx = material_find(material_name)
    if idx == -1:
        print("material not found: "+material_name)
        return
    material = bpy.data.materials[idx]
    node_position = (0, 0)
    bsdf_index = -1

    if property_name == "e_TextureDiffuse0":
        bsdf_index = 0
        node_position = (-350, 280)
    elif property_name == "e_TextureNormal0":
        bsdf_index = 22
        node_position = (-350, 0)
    elif property_name == "e_fShininess0":
        node = material.node_tree.nodes["Principled BSDF"]
        node.inputs[7].default_value = float(property_value)  # type: ignore

    if bsdf_index == -1:
        return

    # get node connected to diffuse
    for node in material.node_tree.nodes:
        if node.label == property_name:
            return

    texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture_node.label = property_name

    texture_path = root_path + "/" + mesh_name + ".mesh/" + \
        material_name + ".material/" + property_value
    if not os.path.exists(texture_path):
        print("texture not found: "+texture_path)
        return

    print(">> Texture "+os.path.basename(texture_path))
    image = bpy.data.images.load(texture_path)
    texture_node.image = image  # type: ignore

    material.node_tree.links.new(
        texture_node.outputs[0], material.node_tree.nodes["Principled BSDF"].inputs[bsdf_index])

    texture_node.location = node_position
