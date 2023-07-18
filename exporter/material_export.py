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
            input7 = mat.node_tree.nodes["Principled BSDF"].inputs[7]
            if input7.default_value != 0:  # type: ignore
                mw.write("%s|%f|%d\n" % (
                    "e_fShininess0", input7.default_value, 0))  # type: ignore
            for node in mat.node_tree.nodes:
                if node.label == "e_TextureDiffuse0":
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
