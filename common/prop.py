# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty
from ..material_panel import on_shader_change
from ..view_panel import on_flag_change, on_ext_change, bone_list_update


def register():
    bpy.utils.register_class(QuailProps)
    bpy.types.Scene.is_flags_open = bpy.props.BoolProperty(
        default=True)
    bpy.types.Scene.quail_props = bpy.props.PointerProperty(
        type=QuailProps, update=on_flag_change)


def unregister():
    if bpy.types.Scene.quail_props != None:
        bpy.utils.unregister_class(QuailProps)
    del bpy.types.Scene.quail_props
    del bpy.types.Scene.is_flags_open


class QuailProps(bpy.types.PropertyGroup):

    bones: bpy.props.EnumProperty(
        items=bone_list_update
    )

    flag_no_collide: BoolProperty(
        name="No Collision",
        description="Does this face cause collisions? (1, 2)",
        update=on_flag_change
    )

    flag_is_invisible: BoolProperty(
        name="Invisible",
        description="Is this face invisible? (2, 4)",
        update=on_flag_change
    )

    is_three: BoolProperty(
        name="3",
        description="Placeholder for (3, 8)",
        update=on_flag_change
    )

    is_four: BoolProperty(
        name="4",
        description="Placeholder for (4, 16)",
        update=on_flag_change
    )

    is_five: BoolProperty(
        name="5",
        description="Placeholder for (5, 32)",
        update=on_flag_change
    )

    is_six: BoolProperty(
        name="6",
        description="Placeholder for (6, 64)",
        update=on_flag_change
    )

    is_seven: BoolProperty(
        name="7",
        description="Placeholder for (7, 128)",
        update=on_flag_change
    )

    is_eight: BoolProperty(
        name="8",
        description="Placeholder for (8, 256)",
        update=on_flag_change
    )

    is_nine: BoolProperty(
        name="9",
        description="Placeholder for (9, 512)",
        update=on_flag_change
    )

    is_ten: BoolProperty(
        name="10",
        description="Placeholder for (10, 1024)",
        update=on_flag_change
    )

    is_eleven: BoolProperty(
        name="11",
        description="Placeholder for (11, 2048)",
        update=on_flag_change
    )

    is_twelve: BoolProperty(
        name="12",
        description="Placeholder for (12, 4096)",
        update=on_flag_change
    )

    is_thirteen: BoolProperty(
        name="13",
        description="Placeholder for (13, 8192)",
        update=on_flag_change
    )

    is_fourteen: BoolProperty(
        name="14",
        description="Placeholder for (14, 16384)",
        update=on_flag_change
    )

    is_fifteen: BoolProperty(
        name="15",
        description="Placeholder for (15, 32768)",
        update=on_flag_change
    )

    is_sixteen: BoolProperty(
        name="16",
        description="Placeholder for (16, 65536)",
        update=on_flag_change
    )

    is_seventeen: BoolProperty(
        name="17",
        description="Placeholder for (17, 131072)",
        update=on_flag_change
    )

    is_eighteen: BoolProperty(
        name="18",
        description="Placeholder for (18, 262144)",
        update=on_flag_change
    )

    is_nineteen: BoolProperty(
        name="19",
        description="Placeholder for (19, 524288)",
        update=on_flag_change
    )

    is_twenty: BoolProperty(
        name="20",
        description="Placeholder for (20, 1048576)",
        update=on_flag_change
    )

    is_twentyone: BoolProperty(
        name="21",
        description="Placeholder for (21, 2097152)",
        update=on_flag_change
    )

    is_twentytwo: BoolProperty(
        name="22",
        description="Placeholder for (22, 4194304)",
        update=on_flag_change
    )

    is_twentythree: BoolProperty(
        name="23",
        description="Placeholder for (23, 8388608)",
        update=on_flag_change
    )

    is_twentyfour: BoolProperty(
        name="24",
        description="Placeholder for (24, 16777216)",
        update=on_flag_change
    )

    is_twentyfive: BoolProperty(
        name="25",
        description="Placeholder for (25, 33554432)",
        update=on_flag_change
    )

    is_twentysix: BoolProperty(
        name="26",
        description="Placeholder for (26, 67108864)",
        update=on_flag_change
    )

    object_types: bpy.props.EnumProperty(
        name="Ext",
        description="Sets the object type for current object",
        update=on_ext_change,
        items=(
            ("mod", "mod", "Sets the object type to MOD"),
            ("mds", "mds", "Sets the object type to MDS"),
            ("ter", "ter", "Sets the object type to TER"),
        ),
    )

    shaders: bpy.props.EnumProperty(
        name="Shader",
        description="Sets the shader for current material",
        items=(
            ("Opaque_MaxCB1.fx", "Opaque_MaxCB1.fx", "Sets the shader"),
            ("AddAlpha_MaxC1.fx", "AddAlpha_MaxC1.fx", "Sets the shader"),
            ("AddAlpha_MaxCB1.fx", "AddAlpha_MaxCB1.fx", "Sets the shader"),
            ("AddAlpha_MaxCBSG1.fx", "AddAlpha_MaxCBSG1.fx", "Sets the shader"),
            ("AddAlpha_MaxCG1.fx", "AddAlpha_MaxCG1.fx", "Sets the shader"),
            ("AddAlpha_MPLBasicA.fx", "AddAlpha_MPLBasicA.fx", "Sets the shader"),
            ("AddAlpha_MPLBasicAT.fx", "AddAlpha_MPLBasicAT.fx", "Sets the shader"),
            ("AddAlpha_MPLBumpA.fx", "AddAlpha_MPLBumpA.fx", "Sets the shader"),
            ("AddAlphaC1Max.fx", "AddAlphaC1Max.fx", "Sets the shader"),
            ("Alpha_MaxC1.fx", "Alpha_MaxC1.fx", "Sets the shader"),
            ("Alpha_MaxCBS1.fx", "Alpha_MaxCBS1.fx", "Sets the shader"),
            ("Alpha_MaxCBSG1.fx", "Alpha_MaxCBSG1.fx", "Sets the shader"),
            ("Alpha_MaxCBSGE1.fx", "Alpha_MaxCBSGE1.fx", "Sets the shader"),
            ("Alpha_MaxCE1.fx", "Alpha_MaxCE1.fx", "Sets the shader"),
            ("Alpha_MPLBasicA.fx", "Alpha_MPLBasicA.fx", "Sets the shader"),
            ("Alpha_MPLBasicAT.fx", "Alpha_MPLBasicAT.fx", "Sets the shader"),
            ("Alpha_MPLBumpA.fx", "Alpha_MPLBumpA.fx", "Sets the shader"),
            ("Alpha_MPLBumpAT.fx", "Alpha_MPLBumpAT.fx", "Sets the shader"),
            ("AlphaSModelC1Max.fx", "AlphaSModelC1Max.fx", "Sets the shader"),
            ("AlphaSModelCBGG1Max.fx", "AlphaSModelCBGG1Max.fx", "Sets the shader"),
            ("Chroma_MaxC1.fx", "Chroma_MaxC1.fx", "Sets the shader"),
            ("Chroma_MaxCB1.fx", "Chroma_MaxCB1.fx", "Sets the shader"),
            ("Chroma_MaxCBS1.fx", "Chroma_MaxCBS1.fx", "Sets the shader"),
            ("Chroma_MaxCBSG1.fx", "Chroma_MaxCBSG1.fx", "Sets the shader"),
            ("Chroma_MaxCBSGE1.fx", "Chroma_MaxCBSGE1.fx", "Sets the shader"),
            ("Chroma_MPLBasicA.fx", "Chroma_MPLBasicA.fx", "Sets the shader"),
            ("Chroma_MPLBasicAT.fx", "Chroma_MPLBasicAT.fx", "Sets the shader"),
            ("Chroma_MPLBumpA.fx", "Chroma_MPLBumpA.fx", "Sets the shader"),
            ("Chroma_MPLBumpAT.fx", "Chroma_MPLBumpAT.fx", "Sets the shader"),
            ("Chroma_MPLGBAT.fx", "Chroma_MPLGBAT.fx", "Sets the shader"),
            ("Opaque_AddAlphaC1Max.fx", "Opaque_AddAlphaC1Max.fx", "Sets the shader"),
            ("Opaque_MaxC1_2UV.fx", "Opaque_MaxC1_2UV.fx", "Sets the shader"),
            ("Opaque_MaxC1.fx", "Opaque_MaxC1.fx", "Sets the shader"),
            ("Opaque_MaxCB1_2UV.fx", "Opaque_MaxCB1_2UV.fx", "Sets the shader"),
            ("Opaque_MaxCBE1.fx", "Opaque_MaxCBE1.fx", "Sets the shader"),
            ("Opaque_MaxCBS_2UV.fx", "Opaque_MaxCBS_2UV.fx", "Sets the shader"),
            ("Opaque_MaxCBS1.fx", "Opaque_MaxCBS1.fx", "Sets the shader"),
            ("Opaque_MaxCBSE1.fx", "Opaque_MaxCBSE1.fx", "Sets the shader"),
            ("Opaque_MaxCBSGE1.fx", "Opaque_MaxCBSGE1.fx", "Sets the shader"),
            ("Opaque_MaxCBST2_2UV.fx", "Opaque_MaxCBST2_2UV.fx", "Sets the shader"),
            ("Opaque_MaxCE1.fx", "Opaque_MaxCE1.fx", "Sets the shader"),
            ("Opaque_MaxCG1.fx", "Opaque_MaxCG1.fx", "Sets the shader"),
            ("Opaque_MaxCSG1.fx", "Opaque_MaxCSG1.fx", "Sets the shader"),
            ("Opaque_MaxLava.fx", "Opaque_MaxLava.fx", "Sets the shader"),
            ("Opaque_MaxSMLava2.fx", "Opaque_MaxSMLava2.fx", "Sets the shader"),
            ("Opaque_MaxWater.fx", "Opaque_MaxWater.fx", "Sets the shader"),
            ("Opaque_MaxWaterFall.fx", "Opaque_MaxWaterFall.fx", "Sets the shader"),
            ("Opaque_MPLBasic.fx", "Opaque_MPLBasic.fx", "Sets the shader"),
            ("Opaque_MPLBasicA.fx", "Opaque_MPLBasicA.fx", "Sets the shader"),
            ("Opaque_MPLBlend.fx", "Opaque_MPLBlend.fx", "Sets the shader"),
            ("Opaque_MPLBlendNoBump.fx", "Opaque_MPLBlendNoBump.fx", "Sets the shader"),
            ("Opaque_MPLBump.fx", "Opaque_MPLBump.fx", "Sets the shader"),
            ("Opaque_MPLBump2UV.fx", "Opaque_MPLBump2UV.fx", "Sets the shader"),
            ("Opaque_MPLBumpA.fx", "Opaque_MPLBumpA.fx", "Sets the shader"),
            ("Opaque_MPLBumpAT.fx", "Opaque_MPLBumpAT.fx", "Sets the shader"),
            ("Opaque_MPLFull.fx", "Opaque_MPLFull.fx", "Sets the shader"),
            ("Opaque_MPLFull2UV.fx", "Opaque_MPLFull2UV.fx", "Sets the shader"),
            ("Opaque_MPLGB.fx", "Opaque_MPLGB.fx", "Sets the shader"),
            ("Opaque_MPLGB2UV.fx", "Opaque_MPLGB2UV.fx", "Sets the shader"),
            ("Opaque_MPLRB.fx", "Opaque_MPLRB.fx", "Sets the shader"),
            ("Opaque_MPLRB2UV.fx", "Opaque_MPLRB2UV.fx", "Sets the shader"),
            ("Opaque_MPLSB.fx", "Opaque_MPLSB.fx", "Sets the shader"),
            ("Opaque_MPLSB2UV.fx", "Opaque_MPLSB2UV.fx", "Sets the shader"),
            ("Opaque_OpaqueRegionCBGG1Max.fx",
             "Opaque_OpaqueRegionCBGG1Max.fx", "Sets the shader"),
            ("Opaque_OpaqueSkinMeshCBGG1Max.fx",
             "Opaque_OpaqueSkinMeshCBGG1Max.fx", "Sets the shader"),
            ("Opaque_OpaqueSModelC1Max.fx",
             "Opaque_OpaqueSModelC1Max.fx", "Sets the shader"),
            ("Opaque_OpaqueSModelCBGG1Max.fx",
             "Opaque_OpaqueSModelCBGG1Max.fx", "Sets the shader"),
            ("OpaqueRegionC1Max.fx", "OpaqueRegionC1Max.fx", "Sets the shader"),
            ("OpaqueRegionCB1Max.fx", "OpaqueRegionCB1Max.fx", "Sets the shader"),
            ("OpaqueSModelCB1Max.fx", "OpaqueSModelCB1Max.fx", "Sets the shader"),
            ("OpaqueSModelCBGG1Max.fx", "OpaqueSModelCBGG1Max.fx", "Sets the shader"),
            ("OpaqueSModelCG1Max.fx", "OpaqueSModelCG1Max.fx", "Sets the shader")
        ),
        update=on_shader_change)
