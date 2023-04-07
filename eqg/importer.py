import os
from . import mds_import, ter_import, mod_import


def eqg_import(eqg_path):
    print("importing eqg", eqg_path)
    ext = os.path.splitext(eqg_path)[1]
    print(ext)
    if ext != ".eqg":
        return

    for sub_path, dirs, files in os.walk(eqg_path):
        mds_import.mds_import(eqg_path, sub_path)
        mod_import.mod_import(eqg_path, sub_path)
        ter_import.ter_import(eqg_path, sub_path)
    pass
