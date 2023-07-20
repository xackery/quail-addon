import bpy
import os


def material_export(quail_path: str, mesh_path: str, materials: bpy.types.IDMaterials):

    for mat in materials:
        if mat is None:
            continue
        material_path = "%s/%s.material" % (mesh_path, mat.name)
        if os.path.exists(material_path):
            continue
        os.makedirs(material_path)
        print("> Material", mat.name)
        if bpy.data.materials.get(mat.name) is None:
            continue
        if mat.name == "":
            continue
        with open("%s/property.txt" % material_path, "w") as mw:
            mw.write(
                "property_name|value|category\n")
            mw.write("%s|%s|%d\n" % ("shaderName", str(mat.get("fx")), 2))

            specular = mat.node_tree.nodes["Principled BSDF"].inputs[7]
            if specular.default_value != 0:  # type: ignore
                mw.write("%s|%f|%d\n" % (
                    "e_fShininess0", specular.default_value, 0))  # type: ignore

            base_color = mat.node_tree.nodes["Principled BSDF"].inputs[0]

            is_texture_diffuse_written = False
            if base_color.is_linked:
                for node_link in base_color.links:  # type: ignore
                    node = node_link.from_node
                    if node.type != "TEX_IMAGE":
                        continue
                    is_texture_diffuse_written = True
                    label = "e_TextureDiffuse0"
                    if node.label.startswith("e_"):
                        label = node.label
                    mw.write("%s|%s|%d\n" % (
                        label, node.image.name, 2))  # type: ignore
                    node.image.save_render(  # type: ignore
                        filepath="%s/%s" % (material_path, node.image.name))  # type: ignore
                    break
            else:
                image = bpy.data.images.new("%s.png" % mat.name, 1, 1)
                pixels = [None] * 16 * 16
                for x in range(16):
                    for y in range(16):
                        rgba = base_color.default_value  # type: ignore
                        pixels[(y * 16+x)] = rgba
                pixels = [chan for px in pixels for chan in px]  # type: ignore
                image.pixels = pixels  # type: ignore
                mw.write("e_TextureDiffuse0|%s.png|2\n" % (
                    mat.name))  # type: ignore
                image.save_render(filepath="%s/%s.png" %
                                  (material_path, mat.name))

            for node in mat.node_tree.nodes:
                if node.label == "e_TextureDiffuse0" and not is_texture_diffuse_written:
                    mw.write("%s|%s|%d\n" % (
                        node.label, node.image.name, 2))  # type: ignore
                    print(">> Texture %s" %
                          node.image.name)  # type: ignore
                    node.image.save_render(  # type: ignore
                        filepath="%s/%s" % (material_path, node.image.name))  # type: ignore

                elif node.label == "e_TextureNormal0":
                    mw.write("%s|%s|%d\n" % (
                        node.label, node.image.name, 2))  # type: ignore
                    print(">> Texture %s" %
                          node.image.name)  # type: ignore
                    node.image.save_render(  # type: ignore
                        filepath="%s/%s" % (material_path, node.image.name))  # type: ignore
