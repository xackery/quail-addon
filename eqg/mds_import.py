import bpy
import os


def mds_import(root_path, path):
    ext = os.path.splitext(path)[1]
    if ext != ".mds":
        return

    print("importing mds", path)
    name = os.path.basename(path)
    # trim prefix _ if it exists
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
                    # create texture
                    texture = bpy.data.textures.new(
                        name=records[2], type='IMAGE')
                    # create texture node
                    texture_node = material.node_tree.nodes.new(
                        'ShaderNodeTexImage')

                    # check if file exists
                    if os.path.exists(root_path+"/"+records[2]):
                        image = bpy.data.images.load(root_path+"/"+records[2])
                        texture.image = image
                        texture_node.image = image
                    # link nodes
                    material.node_tree.links.new(
                        texture_node.outputs[0], material.node_tree.nodes["Principled BSDF"].inputs[0])
                    # set node position
                    texture_node.location = (-350, 280)
                if records[1] == "e_TextureNormal0":
                    # create texture
                    texture = bpy.data.textures.new(
                        name=records[2], type='IMAGE')
                    # create texture node
                    texture_node = material.node_tree.nodes.new(
                        'ShaderNodeTexImage')

                    # check if file exists
                    if os.path.exists(root_path+"/"+records[2]):
                        image = bpy.data.images.load(root_path+"/"+records[2])
                        texture.image = image
                        texture_node.image = image
                    material.node_tree.links.new(
                        texture_node.outputs[0], material.node_tree.nodes["Principled BSDF"].inputs[22])
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
                vert_mesh.append((float(vert_line[0]), float(
                    vert_line[1]), float(vert_line[2])))
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
                normal_mesh.append((int(normal_line[0]), int(
                    normal_line[1]), int(normal_line[2])))
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
