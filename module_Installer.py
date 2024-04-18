bl_info = {
    "name": "Module Installer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Install Panel",
    "description": "Install Python modules from within Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Development"
}


import bpy
import subprocess
import sys

class INSTALL_OT_module(bpy.types.Operator):
    bl_idname = "install.module"
    bl_label = "Install Module"

    
    
    
    def execute(self, context):
        # Blenderが使用するPythonのパスを取得
        python_path = sys.executable

        module_name = bpy.context.scene.module_name
        # pipコマンドを実行してモジュールをインストール
        subprocess.call([python_path, '-m', 'pip', 'install', module_name])
        
        return {'FINISHED'}

class INSTALL_PT_panel(bpy.types.Panel):
    bl_idname = "INSTALL_PT_panel"
    bl_label = "Install Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KSYN"
    bl_options = {"DEFAULT_CLOSED"}

    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(context.scene, "module_name")
        row.operator("install.module")

def register():
    bpy.utils.register_class(INSTALL_OT_module)
    bpy.utils.register_class(INSTALL_PT_panel)
    bpy.types.Scene.module_name = bpy.props.StringProperty(name="Module Name")

def unregister():
    bpy.utils.unregister_class(INSTALL_OT_module)
    bpy.utils.unregister_class(INSTALL_PT_panel)
    del bpy.types.Scene.module_name

if __name__ == "__main__":
    register()