
bl_info = {
    "name": "Randam Material",
    "description": " ",
    "author": "Hydrocallis",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > KSYN Tab",
    "warning": "",
    # "doc_url": "",
    "category": "Object"
    }
import bpy
from bpy.types import (
        Menu,
        Operator,
        Panel,
        PropertyGroup,
        )
import random
from bpy.props import IntProperty,BoolProperty,FloatVectorProperty
from bpy.props import PointerProperty

def get_translang(eng,trans):
    prev = bpy.context.preferences.view
    if prev.language =='ja_JP' and prev.use_translate_interface == True:
        return trans
    else:
        return eng
    
def generate_values(selected_value, choice_list:list, num_values:int, random_frequency:float):
    values = [selected_value]

    for _ in range(1, num_values):
        if random.random() < random_frequency:
            values.append(random.choice(choice_list))
        else:
            values.append(selected_value)
            
    return values
class AH_OP_RandomMaterialOperator(bpy.types.Operator):
    bl_idname = "ksyn.random_material"
    bl_label = get_translang('Random Select Material Index"','選択したマテリアルインデックスをランダムに')
    bl_options = {'REGISTER', 'UNDO',}
    
    
    index_number: IntProperty(name=get_translang('Material Index Number','マテリアルのインデックス番号'), default=1,soft_min =1,) # type: ignore
    random_seed: IntProperty(name=get_translang("Random Seed",'シード'), default=0) # type: ignore
    same_material: BoolProperty(name=get_translang("Same Material",'同じにする'), default=False) # type: ignore # type: ignore
    randma_valse: bpy.props.FloatProperty(name=get_translang('Percentage of same color','同じ色の割合'), default=0.2,soft_min=0,soft_max=1) # type: ignore
    
    def get_randam_valuse_choice(self,selected_value,matlist):
        # selected_value = random.choice(matlist)
        # print('###selected_value',matlist)
        
        choice_matlist = generate_values(selected_value, matlist, len(matlist), self.randma_valse)
        randam_valuse_choice_material = random.choice(choice_matlist)
        # print('###choice_matlist',choice_matlist) bpy.context.scene.aling_material_object = bpy.data.objects["Cube.004"]


        return bpy.data.materials[randam_valuse_choice_material]


    @classmethod
    def poll(cls, context):

        return context.object is not None and context.object.type == 'MESH' and bpy.context.scene.aling_material_object is not None
    
    def execute(self, context):
        # active_object = bpy.context.object
        selected_objects = bpy.context.selected_objects
        # objects_to_change = [obj for obj in selected_objects if obj != active_object]
        
        random.seed(self.random_seed)

        selected_value_mat = random.choice(context.scene.aling_material_object.data.materials)
        selected_value =selected_value_mat.name
        
        if self.same_material:
            random_material = random.choice(context.scene.aling_material_object.data.materials)
        
        for obj in selected_objects:
            if not self.same_material:
                matlist= [mat.name for mat in context.scene.aling_material_object.data.materials]
                random_material = self.get_randam_valuse_choice(selected_value,matlist)
                # random_material = random.choice(context.scene.aling_material_object.data.materials)
            

            try:
                obj.data.materials[self.index_number-1] = random_material
            except IndexError:
                self.report({'WARNING'}, f"Materials Out Of Range.MAX{len(obj.data.materials)}")

        return {'FINISHED'}


class AH_OP_RandomFaceMaterialOperator(Operator):
    bl_idname = "object.random_material"
    
    bl_label = get_translang('Random Face Material"','メッシュのフェイスのマテリアルをランダム')
    bl_options = {'REGISTER', 'UNDO',}
    use_choice_seed : bpy.props.BoolProperty(name=get_translang("Use Choice Seed","シードを変える"),default=True) # type: ignore


    choice_random_seed: IntProperty(name=get_translang("Random Seed",'シード'), default=0) # type: ignore
    # random_seed: IntProperty(name="Random Seed", default=0)
    
    randma_valse: bpy.props.FloatProperty(name=get_translang('Percentage of same color','同じ色の割合'), default=0.2,soft_min=0,soft_max=1) # type: ignore
    selec_face : bpy.props.BoolProperty(name=get_translang("Select Face",'選択面のみ変える')) # type: ignore
    choice_mat : bpy.props.StringProperty(name="Choice Mterial") # type: ignore



    @classmethod
    def poll(cls, context):

        return context.object is not None and context.object.type == 'MESH' and bpy.context.scene.aling_material_object is not None
    
    def draw(self,context):
        self.layout.label(text=f"Choice material : {self.choice_mat}")
        self.layout.prop(self,"use_choice_seed")
        if self.use_choice_seed:
            self.layout.prop(self,"choice_random_seed")
        self.layout.prop(self,"randma_valse")
        self.layout.prop(self,"selec_face")

    def get_randam_valuse_choice(self,selected_value,matlist):
        # selected_value = random.choice(matlist)
        # print('###selected_value',matlist)
        
        choice_matlist = generate_values(selected_value, matlist, len(matlist), self.randma_valse)
        randam_valuse_choice_material = random.choice(choice_matlist)
        # print('###choice_matlist',choice_matlist)

        return bpy.data.materials[randam_valuse_choice_material]

    def add_face_material(self,random_material,atc_matlist,obj,material_slots, face):
        # フェイスにマテリアルを割り当て
        if random_material not in atc_matlist:
            obj.data.materials.append(random_material)
            appendmat_index = material_slots[random_material.name].slot_index
        else:
            appendmat_index = material_slots[random_material.name].slot_index
        
        face.material_index = appendmat_index

    def make_randam_set_material(self,context,obj):
         # マテリアルスロットのリストを取得
        material_slots = obj.material_slots
        
        # MaterialObjectというオブジェクトのマテリアルスロットを取得
        materials = context.scene.aling_material_object.data.materials
        # matlist = [slot.material for slot in context.scene.aling_material_object.material_slots]
        if self.use_choice_seed:
            random.seed(self.choice_random_seed)

        selected_value = random.choice(materials)
        self.choice_mat = selected_value.name

        matlist = generate_values(selected_value, materials, len(materials), self.randma_valse)
 
       
        # メッシュの各フェイスに対してランダムなマテリアルを割り当てる
        for face in obj.data.polygons:
            # ランダムなマテリアルスロットを選択
            # random.seed(self.random_seed)

            random_material = random.choice(matlist)
            atc_matlist = [slot.material for slot in material_slots]
            # print('###face sele',face.select)
            if self.selec_face:
                if face.select ==True:
                    self.add_face_material(random_material,atc_matlist,obj,material_slots, face)
            else:
                self.add_face_material(random_material,atc_matlist,obj,material_slots, face)

    def execute(self, context):
        mode=None

        if bpy.context.mode =="EDIT_MESH":
            bpy.ops.object.mode_set(mode='OBJECT')
            mode="EDIT_MESH"

        # メッシュオブジェクトを取得
        for obj in bpy.context.selected_objects:
            self.make_randam_set_material(context,obj)
       
        if mode =="EDIT_MESH":
            bpy.ops.object.mode_set(mode='EDIT') 
        
        return {'FINISHED'}

class AH_PT_RandomMaterialPanel(Panel):
    bl_idname = "VIEW3D_PT_random_material"
    bl_label = get_translang("Random Material",'ランダムマテリアル')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KSYN"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene, "aling_material_object")
        layout.operator(AH_OP_RandomFaceMaterialOperator.bl_idname)
        layout.operator("ksyn.random_material")
def register():

    bpy.utils.register_class(AH_OP_RandomMaterialOperator)

    bpy.utils.register_class(AH_OP_RandomFaceMaterialOperator)
    bpy.utils.register_class(AH_PT_RandomMaterialPanel)
    bpy.types.Scene.aling_material_object = PointerProperty(type=bpy.types.Object, name=get_translang('Material Object','対象のオブジェクト'), description="Select the Material Object")

def unregister():

    bpy.utils.unregister_class(AH_OP_RandomMaterialOperator)

    bpy.utils.unregister_class(AH_OP_RandomFaceMaterialOperator)
    bpy.utils.unregister_class(AH_PT_RandomMaterialPanel)
    del bpy.types.Scene.aling_material_object


if __name__ == "__main__":
    register()
