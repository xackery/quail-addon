from . import exporter, importer
from . import auto_load
from . import view_panel, material_panel
from .common import prop
auto_load.init()

bl_info = {
    "name": "Quail",
    "author": "xackery",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Export, File > Import",
    "category": "Import-Export",
    "description": "Helper for EverQuest Archives",
}


def register():
    prop.register()
    exporter.register()
    importer.register()
    view_panel.register()
    material_panel.register()
    auto_load.register()


def unregister():
    prop.unregister()
    exporter.unregister()
    importer.unregister()
    view_panel.unregister()
    material_panel.unregister()
    auto_load.unregister()


if __name__ == "__main__":
    register()
