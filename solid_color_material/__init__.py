bl_info = {
    "name": "Solid Color Material",
    "author": "KSYN",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > UI > KSYN",
    "description": "Create simple color textured materials for selected objects",
    "warning": "",
    "wiki_url": "",
    "category": "Material",
}

import bpy,bmesh
import os
from bpy.props import FloatVectorProperty, FloatProperty
import bpy.utils.previews


ksyn_pallet_preview_collections = {}




def assign_material_to_selected_faces(obj, addmat):
    # Retrieve the active object and the selected faces
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    selected_faces = [f for f in bm.faces if f.select]

    # Create a new material and assign it to the selected faces
    me.materials.append(addmat)
    for face in selected_faces:
        face.material_index = len(me.materials) - 1

    # Update the mesh and deselect everything
    bmesh.update_edit_mesh(me)
    
def add_material_to_object(obj, addmat):
    if bpy.context.mode == 'EDIT_MESH':
        # If in edit mode, call the  function
        import bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = [f for f in bm.faces if f.select]
        if selected_faces:
            assign_material_to_selected_faces(obj, addmat)
    else:
        # 選択したオブジェクトのマテリアルを削除
        # 選択したオブジェクトのうちメッシュオブジェクトとカーブオブジェクトのマテリアルを削除
        for obj in bpy.context.selected_objects:
            if obj.type in ['MESH', 'CURVE']:
                obj.data.materials.clear()
                # Add new material
                obj.data.materials.append(addmat)

class KSYN_TextureProperties(bpy.types.PropertyGroup):
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        description="Color of the texture",
        default=(1, 1, 1, 1),
        size=4,
        min=0, max=1,
    )
    
class KSYN_TexturePanel(bpy.types.Panel):
    bl_label = "Solid Color Material"
    bl_idname = "OBJECT_PT_texture_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KSYN"

    def draw(self, context):
        layout = self.layout
        

        # TexturePropertiesを取得
        texture_prop = context.scene.texture_prop

        # Colorを表示
        layout.prop(texture_prop, "color")

        layout.operator("object.create_texture")

        ob = context.object

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 3
            if is_sortable:
                rows = 5

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ADD', text="")
            col.operator("object.material_slot_remove", icon='REMOVE', text="")

            col.separator()

            col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        row = layout.row()

        if ob:
            row.template_ID(ob, "active_material", new="material.new")

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

class KSYN_CreateTextureOperator(bpy.types.Operator):
    bl_idname = "object.create_texture"
    bl_label = "Create Texture"
  
    def execute(self, context):

        # オブジェクトを選択
        addmat = bpy.data.materials.new(name=self.material_name)
        for obj in bpy.context.selected_objects:
            self.add_material(obj, addmat)

        self.save_tex()
        texture_prop = bpy.context.scene.texture_prop

        # print('###cole',len(bpy.context.scene.ksyn_pallet_color_collection))
        if len(ksyn_pallet_preview_collections) != 0:
            for pcoll in ksyn_pallet_preview_collections.values():
                try:
                    bpy.utils.previews.remove(pcoll)
                except KeyError:
                    ksyn_pallet_preview_collections.clear()
                    bpy.context.scene.ksyn_pallet_color_collection.clear()
                    pass
            if hasattr(bpy.context.scene, "ksyn_pallet_color_collection"):
                bpy.context.scene.ksyn_pallet_color_collection.clear()


        return {'FINISHED'}


    def add_material(self, obj, addmat):
        new_material = addmat
        add_material_to_object(obj, addmat)

        # ノードを設定
        new_material.use_nodes = True
        nodes = new_material.node_tree.nodes
        links = new_material.node_tree.links

        # プリンシプルBSDFノードを追加 or 取得
        principled_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if principled_node is None:
            principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            principled_node.location = 0,0

        # イメージテクスチャを追加
        
        self.image_node = nodes.new(type='ShaderNodeTexImage')
        self.image_node.location = -400,0
        self.image_node.image = bpy.data.images.new(name = self.texturename, width=1, height=1)
        self.image_node.image.pixels[:] = self.pixels

        # テクスチャとプリンシプルBSDFノードを接続
        if not any(link.to_node == principled_node for link in self.image_node.outputs[0].links):
            links.new(self.image_node.outputs[0], principled_node.inputs[0])

    def save_tex(self):
        # テクスチャを保存
        if not os.path.exists(self.texture_dir):
            os.makedirs(self.texture_dir)
        texture_name = self.texturename
        texture_path = os.path.join(self.texture_dir, texture_name + ".png")
        self.image_node.image.file_format = 'PNG'
        self.image_node.image.filepath_raw = texture_path
        self.image_node.image.save()
        self.report({'INFO'}, "Save Texture " + texture_path)
        

    def draw(self, context):
        texture_prop = bpy.context.scene.texture_prop
        self.layout.label(text="Color")
        self.layout.prop(texture_prop, "color")
#        self.layout.label(text="Roughness")
#        self.layout.prop(texture_prop, "roughness")

    def invoke(self, context, event):
        # ファイルのパスを取得
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        texture_prop = bpy.context.scene.texture_prop

        red = texture_prop.color[0]
        green = texture_prop.color[1]
        blue = texture_prop.color[2]
        alpha = texture_prop.color[3]
        piccoloer_str = "_{:.2f}_{:.2f}_{:.2f}_{:.2f}".format(red, green, blue, alpha)

        self.texture_dir = os.path.join(directory, "Texture")
        self.pixels = [red, green, blue, alpha]
        self.material_name = "ColorMaterial" + piccoloer_str 
        self.texturename = "ColorTexture" + piccoloer_str 

        return self.execute(context)

classes = [
    KSYN_CreateTextureOperator,
    KSYN_TextureProperties,
    KSYN_TexturePanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.texture_prop = bpy.props.PointerProperty(type=KSYN_TextureProperties)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for pcoll in ksyn_pallet_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    ksyn_pallet_preview_collections.clear()
    
    
    del bpy.types.Scene.texture_prop


if __name__ == "__main__":
    register()