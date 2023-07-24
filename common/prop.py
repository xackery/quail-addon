import bpy
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty
from ..material_panel import on_shader_change
from ..view_panel import on_flag_change


def register():
    bpy.utils.register_class(QuailProps)
    bpy.types.Scene.quail_props = bpy.props.PointerProperty(  # type: ignore
        type=QuailProps)


def unregister():
    bpy.utils.unregister_class(QuailProps)
    del bpy.types.Scene.quail_props  # type: ignore


class QuailProps(bpy.types.PropertyGroup):
    flag_no_collide: BoolProperty(
        name="No Collision",
        description="Does this face cause collisions? (1, 2)",
        update=on_flag_change
    )  # type: ignore

    flag_is_invisible: BoolProperty(
        name="Invisible",
        description="Is this face invisible? (2, 4)",
        update=on_flag_change
    )  # type: ignore

    is_three: BoolProperty(
        name="3",
        description="Placeholder for (3, 8)",
        update=on_flag_change
    )  # type: ignore

    is_four: BoolProperty(
        name="4",
        description="Placeholder for (4, 16)",
        update=on_flag_change
    )  # type: ignore

    is_five: BoolProperty(
        name="5",
        description="Placeholder for (5, 32)",
        update=on_flag_change
    )  # type: ignore

    is_six: BoolProperty(
        name="6",
        description="Placeholder for (6, 64)",
        update=on_flag_change
    )  # type: ignore

    is_seven: BoolProperty(
        name="7",
        description="Placeholder for (7, 128)",
        update=on_flag_change
    )  # type: ignore

    is_eight: BoolProperty(
        name="8",
        description="Placeholder for (8, 256)",
        update=on_flag_change
    )  # type: ignore

    is_nine: BoolProperty(
        name="9",
        description="Placeholder for (9, 512)",
        update=on_flag_change
    )  # type: ignore

    is_ten: BoolProperty(
        name="10",
        description="Placeholder for (10, 1024)",
        update=on_flag_change
    )  # type: ignore

    is_eleven: BoolProperty(
        name="11",
        description="Placeholder for (11, 2048)",
        update=on_flag_change
    )  # type: ignore

    is_twelve: BoolProperty(
        name="12",
        description="Placeholder for (12, 4096)",
        update=on_flag_change
    )  # type: ignore

    is_thirteen: BoolProperty(
        name="13",
        description="Placeholder for (13, 8192)",
        update=on_flag_change
    )  # type: ignore

    is_fourteen: BoolProperty(
        name="14",
        description="Placeholder for (14, 16384)",
        update=on_flag_change
    )  # type: ignore

    is_fifteen: BoolProperty(
        name="15",
        description="Placeholder for (15, 32768)",
        update=on_flag_change
    )  # type: ignore

    is_sixteen: BoolProperty(
        name="16",
        description="Placeholder for (16, 65536)",
        update=on_flag_change
    )  # type: ignore

    object_types: bpy.props.EnumProperty(
        name="Type",
        description="Sets the object type for current material",
        items=(
            ("0", "MOD", "Sets the object type to MOD"),
            ("1", "MDS", "Sets the object type to MDS"),
            ("2", "TER", "Sets the object type to TER"),
        )  # type: ignore
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
        ),  # type: ignore
        update=on_shader_change)  # type: ignore
