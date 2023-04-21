import bpy
import os


def material_load(path: str, mesh: bpy.types.Mesh):
    if not os.path.exists(path+"/material.txt"):
        return
    with open(path+"/material.txt") as f:
        lines = f.readlines()
        # skip first line
        lines.pop(0)
        for line in lines:
            records = line.split("|")
            name = records[1].rstrip()
            if bpy.data.materials.get(records[1]) is None:
                material_add(name, records[2], records[3])
            mesh.materials.append(bpy.data.materials[name])


def material_property_load(root_path: str, path: str, mesh: bpy.types.Mesh):
    if not os.path.exists(path+"/material_property.txt"):
        return
    with open(path+"/material_property.txt") as f:
        lines = f.readlines()
        # skip first line
        lines.pop(0)
        for line in lines:
            records = line.split("|")
            material_property_add(
                root_path, records[0], records[1], records[2], records[3])
            if records[1] == "e_TextureDiffuse0" and records[2][-4:] == ".dds" and os.path.exists(root_path+"/"+records[2][:-4]+".txt"):
                with open(root_path+"/"+records[2][:-4]+".txt") as f:
                    anim_data = f.read()
                    material = bpy.data.materials[records[0]]
                    material["anim_data"] = anim_data
                    # iterate anim_data line by line
                    # skip first line
                    lines = anim_data.splitlines()
                    lines.pop(0)
                    for line in lines:
                        if records[2] == line:
                            continue
                        if line[-4:] != ".dds":
                            continue
                        line = line[:-4]
                        print("analyzing anim data line "+line)

                        if bpy.data.materials.find(line) == -1:
                            print("adding anim material")
                            # add material
                            material_add(
                                line, records[1], records[2].strip())
                            material_property_add(
                                root_path, line, records[1].rstrip(), line.rstrip()+".dds", records[3].rstrip())


def material_add(material_name, flags, shader):
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material["flags"] = flags
    material["fx"] = shader
    if shader == "Opaque_MaxCB1.fx":
        pass
    # set specular to 0
    material.specular_intensity = 0
    return material


def material_property_add(root_path, material_name, property_name, property_value, property_category):
    if material_name == "":
        return
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
        material.node_tree.nodes["Principled BSDF"].inputs[7].default_value = float(  # type: ignore
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
