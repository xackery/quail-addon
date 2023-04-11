import bpy
import os
from ..common.material import add_material, add_material_property
from mathutils import Vector, Quaternion


def mod_export(root_path):
    for collection in bpy.data.collections:
        if collection.name.endswith(".mod"):
            path = root_path + "/_" + collection.name
            if not os.path.exists(path):
                os.makedirs(path)
            for obj in collection.objects:
                if obj.type != "MESH":
                    continue
                with open(path+"/material.txt", "w") as mw:
                    mw.write("name|flag|shader_name\n")
                    for mat in obj.material_slots:
                        if mat.material is None:
                            continue
                        if bpy.data.materials.get(mat.material.name) is None:
                            continue
                        print(mat.material["fx"])
                        mw.write("%s|%s|%s\n" % (
                                 mat.material.name, mat.material["fx"], mat.material["flags"]))
                        with open(path+"/material_property.txt", "w") as mw:
                            mw.write(
                                "material_name|property_name|value|category\n")
                            if mat.material.node_tree.nodes["Principled BSDF"].inputs[7].default_value != 0:
                                mw.write("%s|%s|%f|%d\n" % (
                                    mat.material.name, "e_fShininess0", mat.material.node_tree.nodes["Principled BSDF"].inputs[7].default_value, 2))
                            for node in mat.material.node_tree.nodes:
                                if node.label == "e_TextureDiffuse0":
                                    mw.write("%s|%s|%s|%d\n" % (
                                        mat.material.name, node.label, node.image.name, 2))
                                elif node.label == "e_TextureNormal0":
                                    mw.write("%s|%s|%s|%d\n" % (
                                        mat.material.name, node.label, node.image.name, 2))

                mesh = obj.to_mesh()
                with open(path+"/vertex.txt", "w") as vw:
                    vw.write("position|normal|uv|uv2|tint\n")
                    mesh.uv_layers.active = mesh.uv_layers[0]
                    mesh.uv_layers.active_index = 0
                    mesh.uv_layers[0].active_render = True
                    uv = mesh.uv_layers[0].data
                    for i in range(len(mesh.vertices)):
                        vert = mesh.vertices[i]
                        vw.write("%0.2f,%0.2f,%0.2f|%0.2f,%0.2f,%0.2f|%0.2f,%0.2f|%0.2f,%0.2f|%0.2f,%0.2f,%0.2f,%0.2f\n" % (
                            vert.normal.x, vert.normal.y, vert.normal.z,
                            vert.co.x, vert.co.x, vert.co.z,
                            uv[i].uv.x, uv[i].uv.y,
                            0, 0,
                            120, 120, 120, 255))
