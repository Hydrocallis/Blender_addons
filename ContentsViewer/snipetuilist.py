import bpy,os,pickle,pathlib, pprint , re
from bpy.props import StringProperty, IntProperty, CollectionProperty ,BoolProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel
from bpy.types import (
                        Panel,
                        Menu,
                        Operator,
                        PropertyGroup,
                        AddonPreferences,
                        )


def open_folder():
    path =bpy.context.scene.textsnippets_my_list[get_listindex()].list_script_prop
    if os.name == "nt":
        os.startfile(path)
    elif os.name == "posix":
        os.system('xdg-open "%s"' % path)
    elif os.name == "mac":
        os.system('open "%s"' % path)
    return path

def insert_snippet(filepath):

    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as f:
            txt = f.read()
        bpy.ops.text.insert(text = txt)

def poll():
    return bpy.context.scene.textsnippets_my_list

def listlengs():
    return len(bpy.context.scene.textsnippets_my_list)

def rangeadd(name, list_script_prop,list_script_prop2,list_script_prop3):
    lists= bpy.context.scene.textsnippets_my_list
    totallist = len(lists)
    lists.add()
    lists[totallist].name = name
    lists[totallist].list_script_prop = list_script_prop
    lists[totallist].list_script_prop2 = list_script_prop2
    lists[totallist].list_script_prop3 = list_script_prop3


def change(changename):

    extension = os.path.splitext(os.path.basename(get()[0]))[1]
    new_path = os.path.join(get()[3],changename+extension)  
    os.rename(get()[1],new_path) 
    reload()


def remove_prop():
    listindex= bpy.context.scene.textsnippets_list_index
    lists= bpy.context.scene.textsnippets_my_list
    lists.remove(listindex)


def get():
    lists= bpy.context.scene.textsnippets_my_list
       
    if lists.items()==[]:
        return False
    else:
        x = lists[bpy.context.scene.textsnippets_list_index]
        informatino = (x.name, x.list_script_prop, x.list_script_prop2, x.list_script_prop3)
        return informatino

def get_pytxtlists():
    direandfilelists = []
    addon_prefs = bpy.context.preferences.addons["ContentsViewer"].preferences
    pathlist = [addon_prefs.filepath]
    # pathlist = [os.path.dirname(__file__),"snippets"]
    path = os.path.join(*pathlist)
    pathlibpath = pathlib.Path(path)
    direand_pytxt_filelists = sorted([p for p in pathlibpath.glob('**/*') if re.search('/*\.(py|txt)', str(p))])
    for name in direand_pytxt_filelists:
        dirpath = os.path.dirname(name)
        subdirname = os.path.basename(os.path.dirname(name))
        direandfilelists.append((str(name),os.path.basename(name),dirpath,subdirname))
        # print("###1",name)
        # print("###2",os.path.basename(name))
        # print("###3",dirpath)
        # print("###4",subdirname)
    return direandfilelists

def reload():
    direandfilelists = get_pytxtlists()
    bpy.context.scene.textsnippets_my_list.clear()
    [rangeadd(i[1],str(i[0]), i[3], i[2]) for i in direandfilelists]

def get_listindex():
    return bpy.context.scene.textsnippets_list_index


def moveindex(new_index, list_length):
    bpy.context.scene.textsnippets_list_index = max(0, min(new_index, list_length))


class TEXTSNIPPETSUILIST_ListItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    name: StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled") # type: ignore

    list_script_prop: StringProperty(
           name="Any other property you want",
           description="",
           
           default="") # type: ignore

    list_script_prop2: StringProperty(
           name="Any other property you want",
           description="",
           
           default="") # type: ignore

    list_script_prop3: StringProperty(
           name="Any other property you want",
           description="",
           
           default="") # type: ignore
           


class TEXTSNIPPETSUILIST_OT_loadfile(Operator):

    bl_idname = "textsnippets_my_list.loadfile"
    bl_label = "load item"

    @classmethod
    def poll(cls, context):
        if poll() == True:

            return False 
        else:
            return True

    def execute(self, context):
        
        reload()

        return{'FINISHED'}


class TEXTSNIPPETSUILIST_OT_savefile(Operator):

    bl_idname = "textsnippets_my_list.savefile"
    bl_label = "save item"

    @classmethod
    def poll(cls, context):
        # return poll()
        return False

    def execute(self, context):
        filepath = __file__
        writelist = [(i[0],i[1].name,i[1].list_script_prop) for i in enumerate(bpy.context.scene.textsnippets_my_list)]
        text = os.path.dirname(filepath)
        text = os.path.join(text, "text.txt")

        f = open(text, 'wb')
        list_row = writelist
        pickle.dump(list_row, f)




        return{'FINISHED'}
   

class TEXTSNIPPETSUILIST_OT_get(Operator):
    """Add a new item to the list."""

    bl_idname = "textsnippets_my_list.get"
    bl_label = "get a new item"

    @classmethod
    def poll(cls, context):
        text = bpy.data.texts
        if len(text) > 0 and len(poll())> 0:
            actareatext = True
        else:
            actareatext = False

        
        if actareatext == True:
            return True


    def execute(self, context):
        props = bpy.context.scene.textsnippets_uiprops
        print('###poll',poll())

        print(len(poll()))

        insert_snippet(get()[1])

        self.report({'INFO'},"insert")
        

        return{'FINISHED'}

class TEXTSNIPPETSUILIST_OT_openfile(Operator):
    """Add a new item to the list."""

    bl_idname = "textsnippets_my_list.openfile"
    bl_label = "open file"

    @classmethod
    def poll(cls, context):
        text = bpy.data.texts
        if len(text) > 0 and len(poll())> 0:
            actareatext = True
        else:
            actareatext = False

        
        if actareatext == True:
            return True


    def execute(self, context):
        file_path = open_folder()

        self.report({'INFO'}, file_path)
        

        return{'FINISHED'}


class TEXTSNIPPETSUILIST_OT_NewItem(Operator):
    """Add a new item to the list."""

    bl_idname = "textsnippets_my_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):

        props = bpy.context.scene.textsnippets_uiprops


        rangeadd(props.name2, props.script_prop)

        

        return{'FINISHED'}


class TEXTSNIPPETSUILIST_OT_change(Operator):
    """Add a new item to the list."""

    bl_idname = "textsnippets_my_list.change"
    bl_label = "change a new item"
    @classmethod
    def poll(cls, context):
        return poll()

    def execute(self, context):
        scene = context.scene

        props = bpy.context.scene.textsnippets_uiprops
        bpy.types.Scene.textsnippets_uiprops

        change(props.name2)

        

        return{'FINISHED'}
    

class TEXTSNIPPETSUILIST_OT_delete(Operator):
    """Add a new item to the list."""

    bl_idname = "textsnippets_my_list.de"
    bl_label = "de a new item"

    @classmethod
    def poll(cls, context):
        return poll()

    def execute(self, context):
        scene = context.scene

        remove_prop()
        

        return{'FINISHED'}


class TEXTSNIPPETSUILIST_OT_MoveItem(Operator):
    """Move an item in the list."""

    bl_idname = "textsnippets_my_list.move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),)) # type: ignore

    @classmethod
    def poll(cls, context):
        return poll()

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = get_listindex()

        list_length = listlengs() - 1  # (index starts at 0)

        new_index = index + (-1 if self.direction == 'UP' else 1)

        moveindex(new_index, list_length)

    def execute(self, context):
        textsnippets_my_list = context.scene.textsnippets_my_list
        index = get_listindex()

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        textsnippets_my_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}


class TEXTSNIPPETSUILISTMY_UL_List(UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'
        row = layout.row()

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row.label(text=f"{index}_[{item.name}]")
            row.label(text=f"{item.list_script_prop2}")

  
        elif self.layout_type in {'GRID'}:
            row.alignment = 'CENTER'
            row.label(text="", icon = custom_icon)


class TEXTSNIPPETSUILIST_PT_ListExample(Panel):
    """Demo panel for UI list Tutorial."""
    bl_label = 'uilisttest'
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'uilisttest'



    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = bpy.context.scene.textsnippets_uiprops
        row =layout.row()
        if  listlengs() > 0  and get_listindex() < listlengs():
            box = layout.box()
            box.label(text = bpy.context.scene.textsnippets_my_list[get_listindex()].name)
            box.label(text = bpy.context.scene.textsnippets_my_list[get_listindex()].list_script_prop)
            box.operator("textsnippets_my_list.openfile")
            box.label(text = bpy.context.scene.textsnippets_my_list[get_listindex()].list_script_prop2)
            row = layout.row()
        else:
            box = layout.box()
            box.label(text = "please select active index")
            row = layout.row()

        row.template_list("TEXTSNIPPETSUILISTMY_UL_List", "The_List", scene,
                          "textsnippets_my_list", scene, "textsnippets_list_index")

        col = row.column(align=True)
        col.operator("textsnippets_my_list.loadfile",text = "", icon="FILE_NEW")
        # col.operator("textsnippets_my_list.savefile",text = "", icon="CURRENT_FILE")
        # col.operator("textsnippets_my_list.new_item",text = "", icon="ADD")
        # col.operator("textsnippets_my_list.de",text = "", icon="PANEL_CLOSE")
        # col.operator('textsnippets_my_list.move_item',text = "", icon="TRIA_UP").direction = 'UP'
        # col.operator('textsnippets_my_list.move_item',text = "", icon="TRIA_DOWN").direction = 'DOWN'
        col.operator('textsnippets_my_list.get', text = "", icon="IMPORT")
        # col.separator()
            
        col = layout.row()
        col.operator("textsnippets_my_list.change",text = "", icon="FILE_REFRESH")
        col.prop(props, "name2")
        # col = layout.row()
        # col.prop(props, "script_prop")
        # col = layout.row()
        # col.prop(props, "run_bool")
        # col = layout.row()
        # col.prop(props, "set_list_comprehension")
        # if props.set_list_comprehension ==True:

        #     col = layout.row()
        #     col.prop(props, "set_list_comprehension_string")
        #     col = layout.row()
        #     col.prop(props, "set_list_comprehension_if_string")
        #     col = layout.row()
        #     col.prop(props, "set_list_comprehension_print_bool")
        #     col = layout.row()
        #     col.prop(props, "set_list_comprehension_enumerate_bool")
        #     col = layout.row()



class TEXTSNIPPETSUILISTmyuiPropertyGroup(bpy.types.PropertyGroup):

    name2: StringProperty(
           name="name",
           description="A name for this item",
           default="Untitled") # type: ignore

    script_prop: StringProperty(
           name="script",
           description="",
           
           default="aaaUntitled") # type: ignore
           
    int2: IntProperty(
           name="",
           description="",
           default=9) # type: ignore
           
    newindex_int2: IntProperty(
           name="",
           description="",
           default=9) # type: ignore
    
    run_bool : BoolProperty(
        name="run",
               ) # type: ignore

    set_list_comprehension : BoolProperty(
        name="list comprehension",
               ) # type: ignore
    
    set_list_comprehension_print_bool : BoolProperty(
        name="print list comprehension",
               ) # type: ignore
    
    set_list_comprehension_enumerate_bool : BoolProperty(
        name="enumerate list comprehension",
               ) # type: ignore

    set_list_comprehension_string: StringProperty(
           name="op1 list",
           description="if enumerate use inut i[1]",
           
           default="i") # type: ignore

    set_list_comprehension_if_string: StringProperty(
           name="op2 if list",
           description="if enumerate use inut i[1]",
           
           default="") # type: ignore





