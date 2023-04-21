import bpy
import os
from .material import material_add, material_property_add


def mesh_export(root_path):
    for collection in bpy.data.collections:
        print("Collection", collection.name)
        if not collection.name.endswith(".mod"):
            continue
        path = root_path + "/_" + collection.name
        if not os.path.exists(path):
            print("Creating", path)
            os.makedirs(path)
        me = open(path+"/mesh.txt", "w")
        me.write("name\n")
        with open(path+"/info.txt", "w") as mi:
            mi.write("version=3\n")
        for obj in collection.objects:
            if obj.type != "MESH":
                continue
            me.write(obj.name+"\n")
            obj_export(obj, root_path, path)
        me.close()


def obj_export(obj: bpy.types.Object, root_path: str, path: str):
    print("  Mesh", obj.name)
    mesh = obj.to_mesh()
    material_export(mesh.materials, root_path, path)
    with open("%s/%s_vertex.txt" % (path, obj.name), "w") as vw:
        vw.write("position|normal|uv|uv2|tint\n")
        mesh.uv_layers.active = mesh.uv_layers[0]
        mesh.uv_layers.active_index = 0
        mesh.uv_layers[0].active_render = True
        uv = mesh.uv_layers[0].data
        for i in range(len(mesh.vertices)):
            vert = mesh.vertices[i]
            vw.write("%0.3f,%0.3f,%0.3f|%0.3f,%0.3f,%0.3f|%0.3f,%0.3f|%0.3f,%0.3f|%d,%d,%d,%d\n" % (
                vert.co.x, vert.co.y, vert.co.z,
                vert.normal.x, vert.normal.y, vert.normal.z,
                uv[i].uv.x, uv[i].uv.y,
                0, 0,
                120, 120, 120, 255))
    with open("%s/%s_triangle.txt" % (path, obj.name), "w") as tw:
        tw.write("index|flag|material_name\n")
        for poly in mesh.polygons:
            flag = 0

            if len(mesh.face_maps) > 0 and len(mesh.face_maps[0].data) >= poly.index:
                name = obj.face_maps[mesh.face_maps[0].data[poly.index].value].name
                flag = name[5:]
            tw.write("%d,%d,%d|%s|%s\n" % (
                poly.vertices[0], poly.vertices[1], poly.vertices[2], flag, mesh.materials[poly.material_index].name))


def material_export(materials: bpy.types.IDMaterials, root_path: str, path: str):
    with open(path+"/material.txt", "w") as maw:
        maw.write("id|material_name|flag|shader_name\n")
        for mat in materials:
            if mat is None:
                continue
            print("    Material", mat.name, mat["fx"].rstrip(), mat["flags"])
            if bpy.data.materials.get(mat.name) is None:
                continue
            if mat.name == "":
                continue
            maw.write("%d|%s|%s|%s\n" % (
                0, mat.name, mat["flags"], mat["fx"].rstrip()))
            with open(path+"/material_property.txt", "w") as mw:
                mw.write(
                    "material_name|property_name|value|category\n")
                if mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value != 0:
                    mw.write("%s|%s|%f|%d\n" % (
                        mat.name, "e_fShininess0", mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value, 0))
                for node in mat.node_tree.nodes:
                    if node.label == "e_TextureDiffuse0":
                        mw.write("%s|%s|%s|%d\n" % (
                            mat.name, node.label, node.image.name, 2))  # type: ignore
                        node.image.save_render(
                            filepath=root_path+"/"+node.image.name)

                    elif node.label == "e_TextureNormal0":
                        mw.write("%s|%s|%s|%d\n" % (
                            mat.name, node.label, node.image.name, 2))  # type: ignore
                        node.image.save_render(
                            filepath=root_path+"/"+node.image.name)
