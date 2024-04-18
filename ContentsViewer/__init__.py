# ----- BEGIN GPL LICENSE BLOCK -----
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ----- END GPL LICENSE BLOCK -----

bl_info = {
    'name': "cus Contents Viewer",
    'author': "Mackraken", "batFinger"
    'version': (0, 1, 5),
    'blender': (2, 80, 0),
    'location': "Text Editor > Right Click",
    'warning': "",
    'description': "List text's classes, definitions and create snippets",
    'wiki_url': "https://sites.google.com/site/aleonserra/home/scripts/class-viewer",
    'category': "Text Editor"}




import bpy, os, sys, pathlib, pprint, glob, re
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty
# print(30*"-")
# ※１	
if "bpy" in locals():
	import importlib
	reloadable_modules = [
    "snipetuilist",	
	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])

# ※２
from .snipetuilist import *
import inspect

snipetuilistclasses = inspect.getmembers(snipetuilist,inspect.isclass)

filesnipetuilistclasseslist = [i[1] for i in snipetuilistclasses if str(i[0]).startswith('TEXTSNIPPETSUILIST') == True]


class ReloadUnityModuluse():
    # リロードモジュール　開始
    def get_all_py_files(self, directory):
        import os

        py_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        return py_files

    def reload_unity_modules(self, name="", debug=False):
        

        # utilsディレクトリおよびそのサブディレクトリ内のすべての.pyファイルを取得
        utils_py_files = self.get_all_py_files(os.path.join(__path__[0], "utils"))

        # ファイルパスからモジュール名を抽出し、アルファベット順にソート
        utils_modules = sorted([os.path.splitext(os.path.relpath(file, __path__[0]))[0].replace(os.path.sep, ".") for file in utils_py_files])

        # 各モジュールを動的にリロード
        for module in utils_modules:
            # モジュール名とサブフォルダの取得
            module_parts = module.rsplit('.', 1)
            module_name = module_parts[-1]
            sub_folder = module_parts[0] + '.' if len(module_parts) == 2 else ''

            # 余分なドットを取り除いて、モジュールの相対インポートとリロード
            impline = f"from .{sub_folder.rstrip('.')} import {module_name}"
            exec(impline)
            if debug==True:
                print("### impline:", impline)
                print(f"###{name} reload module:", module_name)
            importlib.reload(eval(module_name))

if 'bpy' in locals():
    ReloadUnityModuluse().reload_unity_modules(name=bl_info['name'],debug=False)

from .utils.get_translang import get_translang
from .utils.get_select_text import get_select_text

def make_path():
    addon_prefs = bpy.context.preferences.addons["ContentsViewer"].preferences
    
    pathlist = [addon_prefs.filepath]

    path = os.path.join(*pathlist)
    pathlibpath = pathlib.Path(path)
    # pprint.pprint([p.name for p in pathlibpath.iterdir() if p.is_file()])
    intrdirfiles = [p.name for p in pathlibpath.iterdir() if p.is_file()]

    # intrdirfiles = pathlibpath.glob('*')
    # print('###golb',list(intrdirfiles))
    return path,intrdirfiles

def path_list(self, context):
    path,intrdirfiles=make_path()

    p_temp = pathlib.Path(path)
   
    return [(str(p.resolve()),str(p.stem),"") for p in p_temp.iterdir()]
    # return [("","",""),]

def open_folder():
    path,intrdirfiles=make_path()

    if os.name == "nt":
        os.startfile(path)
    elif os.name == "posix":
        os.system('xdg-open "%s"' % path)
    elif os.name == "mac":
        os.system('open "%s"' % path)

def get_snippets():
    path,intrdirfiles=make_path()

    snippets = []
    if not os.path.exists(path): return snippets

    files = os.listdir(path)

    for file in files:

        if file[-3::] == "txt":
            snippets.append(file[0:-4])

        elif file[-2::] == "py":
            snippets.append(file[0:-3])
            
    return snippets

def enum_get_snippets(self, context):
    path,intrdirfiles=make_path()

    snippets = []
    if not os.path.exists(path): return snippets


    for file in intrdirfiles:
        # print('###str',str(file))

        if str(file)[-3::] == "txt":
            snippets.append(str(file)[0:-4])

        elif str(file)[-2::] == "py":
            snippets.append(str(file)[0:-3])
        
            
    enum_snippets = []

    for esnipe in snippets:
        # result = re.sub(r"[^a-zA-Z0-9 -~]", "", esnipe)
        enum_snippets.append((esnipe, esnipe,""))
    return enum_snippets

def current_text(context):
    if context.area.type == "TEXT_EDITOR":
        return context.area.spaces.active.text

def text_selection(context):
    txt = current_text(context)
    sel = ""

    if txt:
        sline = txt.current_line
        endline = txt.select_end_line
        if sline == endline: return sel

        rec = 0
        for i, l in enumerate(txt.lines):
            i=i+1
            line = l.body + "\n"
            if l == sline or l==endline:
                if rec == 0:
                    rec = 1
                    sel += line
                    continue
            if rec:
                sel += line
                if l == sline or l==endline:
                    break
    return sel

# ここでデフのリスト作成する
def getfunc(txt, sort = True):
    if not txt: return []

    defs = []
    classes = []
    comments = []
    tipoclass = "class "
    tipodef = "def "
    tipocomment = "# "

    for i, l in enumerate(txt.lines):
        i=i+1
        line = l.body

        ### find classes
        find = line.find(tipoclass)
        if find==0:
            class_name = line[len(tipoclass):line.find("(")]

            classes.append([class_name, i, []])
            continue

        #すべての関数を抽出find defs
        find = line.find(tipodef)
        if find>=0:
            defname = line[find+len(tipodef):line.find("(")]
            
        # クラス以外の普通の関数をアペンド
        if find ==0:

            defs.append([defname, i])
            continue

        # クラス内の関数をアペンド※インシデントが４つ以上の関数を習得
        if classes and find>0 and find<5:
            classes[-1][2].append([defname, i])
            if sort: classes[-1][2] = sorted(classes[-1][2])
            continue


        #find comments
        find = line.find(tipocomment)
        if find>=0:
            comname = line[find+len(tipocomment)::].strip()
            comments.append([comname, i])
            continue

    if sort: return sorted(defs), sorted(classes), sorted(comments)
    return defs, classes, comments

def linejump(self, context):
    bpy.ops.text.jump(line = self.line)

def findword(self, context):
    if self.findtext:
        spc = context.area.spaces.active
        bpy.ops.text.jump(line=1)
        spc.find_text = self.findtext
        try:
            bpy.ops.text.find()
        except:
            pass

# get error from traceback
def get_error():
    if hasattr(sys, "last_traceback") and sys.last_traceback:
        i = 0
        last=sys.last_traceback.tb_next
        prev = None
        while last:
            i+=1
            prev = last
            last = last.tb_next
            if i>100:
                print("bad recursion")
                return False
        if prev:
            return prev.tb_lineno
        else:
            return sys.last_traceback.tb_lineno
    else:
        if sys.last_value:
            return sys.last_value.lineno
    return False

class ClassViewerProps(bpy.types.PropertyGroup):
    line: IntProperty(min=1, update=linejump) # type: ignore
    findtext: StringProperty(name = "Find Text", default = "" , update = findword) # type: ignore
    show_defs: BoolProperty(name="Show Sub Defs", default=True, description="Shows definitions under classes.") # type: ignore

bpy.utils.register_class(ClassViewerProps)
bpy.types.Scene.class_viewer = PointerProperty(type=ClassViewerProps)

def insert_snippet(name):
    path,intrdirfiles=make_path()

    pathname = os.path.join(path, name+".*")
    filepath = glob.glob(pathname)[0]
        

    # filepath = os.path.join(path, name + ".py")

    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as f:
            txt = f.read()
        bpy.ops.text.insert(text = txt)

def save_snippet(name, txt):
    path,intrdirfiles=make_path()

    name = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', name)

    filepath = os.path.join(path, name + ".py")
    with open(filepath, "w", encoding='utf-8') as f:
        f.write(txt)


class KSYNcontentsvieweraddonPreferences(AddonPreferences):

    bl_idname = __package__

    filepath: StringProperty(
        name="Snipets File Path",
        default="C:/",
        subtype='FILE_PATH',

    )# type: ignore
    move_file_location: BoolProperty(
        name="Example Boolean",
        default=False,
    )# type: ignore



    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons["ContentsViewer"].preferences
        layout.prop(addon_prefs, "filepath", text=get_translang("Snipets File location","スニペットファイルの場所"))
      

class TEXT_OT_class_viewer_search(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "text.class_viewer_search"
    bl_label = "Class Viewer_search"

    bl_property = "my_enumsearch"
    items = [("s","",""),("","",""),("","","")]
    my_enumsearch: bpy.props.EnumProperty(items = enum_get_snippets, name='New Name',) # type: ignore
    

    @classmethod
    def poll(cls, context):
        return True  # This prevents executing the operator if we didn't select a material


    def execute(self, context):
        # print('###test',self.my_enumsearch)
        insert_snippet(self.my_enumsearch)
     

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

class TEXT_OT_class_viewer(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "text.class_viewer"
    bl_label = "Class Viewer"

    line: IntProperty(default=0, options={'HIDDEN'}) # type: ignore
    cmd: StringProperty(default="", options={'HIDDEN'}) # type: ignore
    snippet: StringProperty(default="", options={'HIDDEN'}) # type: ignore
    snippetname: StringProperty(name="Snippet Name") # type: ignore

    


    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    def execute(self, context):
        line = self.line
        cmd = self.cmd
        snippet = self.snippet

        if cmd == "ADD_SNIPPET":
            name = self.snippetname.strip()
            sel = text_selection(context)

            if not sel:
                start_text,select_text,end_text = get_select_text()
                sel = select_text
            if name and sel:
                save_snippet(name, sel)

        if cmd == "<open folder>":
            open_folder()

 

        elif cmd == "LAST_ERROR":
            line = get_error()
            if not line:
                self.report({'WARNING'}, "No Last Error")
            else:
                self.report({'WARNING'}, sys.last_value.args[0])


        if line>0:
            bpy.ops.text.jump(line=line)

        if snippet:
            insert_snippet(snippet)

        self.cmd = 	""
        self.line = -1
        self.snippet = ""
        self.snippetname = ""

        return {'FINISHED'}


    def invoke(self, context, event):
        if self.cmd == "ADD_SNIPPET":
            if text_selection(context):
                wm = context.window_manager
                return wm.invoke_props_dialog(self)
            else:
                start_text,select_text,end_text = get_select_text()
                if select_text:
                    wm = context.window_manager
                    return wm.invoke_props_dialog(self)
                    
                else:
                    self.report({'INFO'}, "Select some text.")
        else:
            return self.execute(context)
        self.cmd = 	""
        self.line = -1
        self.snippet = ""
        self.snippetname = ""
        return {'FINISHED'}

class TEXT_MT_def_viewer(bpy.types.Menu):
    bl_idname = "TEXT_MT_def_viewer"
    bl_label = "Defs Viewer Menu"

    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.type=="TEXT_EDITOR" and context.area.spaces.active.text

    def draw(self, context):
        layout = self.layout
        txt = current_text(context)
        items = getfunc(txt, 1)[0]

        for it in items:
            layout.operator("text.class_viewer",text=it[0]).line = it[1]

class TEXT_MT_class_viewer(bpy.types.Menu):
    bl_idname = "TEXT_MT_class_viewer"
    bl_label = "Class Viewer Menu"

    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.type=="TEXT_EDITOR" and context.area.spaces.active.text

    def draw(self, context):
        layout = self.layout
        txt = current_text(context)
        items = getfunc(txt)[1]
        showdefs = context.scene.class_viewer.show_defs

        for it in items:
            cname = it[0]
            cline = it[1]
            cdefs = it[2]
            layout.operator("text.class_viewer",text=cname).line = cline
            if showdefs:
                for d in cdefs:
                    dname = "      " + d[0]
                    dline = d[1]
                    layout.operator("text.class_viewer",text=dname).line = dline
        layout.separator()
        layout.prop(context.scene.class_viewer, "show_defs")

class TEXT_MT_comment_viewer(bpy.types.Menu):
    bl_idname = "TEXT_MT_comment_viewer"
    bl_label = "Comments Viewer Menu"

    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.type=="TEXT_EDITOR" and context.area.spaces.active.text

    def draw(self, context):
        layout = self.layout
        txt = current_text(context)
        items = getfunc(txt)[
            2]

        for it in items:
            layout.operator("text.class_viewer",text=it[0]).line = it[1]

class TEXT_MT_snippet_viewer(bpy.types.Menu):
    bl_idname = "TEXT_MT_snippet_viewer"
    bl_label = "Snippets Viewer Menu"

    @classmethod
    def poll(cls, context):
        path,intrdirfiles=make_path()
        return os.path.exists(path)

    def draw(self, context):
        layout = self.layout

        snippets = get_snippets()
        # print('###',snippets)
        layout.operator("text.class_viewer_search", text = "search",icon="ZOOM_ALL")
        layout.separator()

        for item in snippets:
            layout.operator("text.class_viewer", text = item,icon="WORDWRAP_ON").snippet = item

        layout.separator()
        layout.operator("text.class_viewer_search", text = "search",icon="ZOOM_ALL")

def draw_items(self, context):
    self.layout.separator()
    self.layout.menu("TEXT_MT_def_viewer", text="Defs")
    self.layout.menu("TEXT_MT_class_viewer", text="Classes")
    self.layout.menu("TEXT_MT_comment_viewer", text="Comments")
    # Snipet
    self.layout.separator()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("text.class_viewer_search", text = "search",icon="ZOOM_ALL")
    self.layout.operator("text.class_viewer", text = "Open Folder",icon="FILEBROWSER").cmd = "<open folder>"
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("text.class_viewer", text="Save a Snippet",icon="FILE_NEW").cmd="ADD_SNIPPET"
    self.layout.menu("TEXT_MT_snippet_viewer", text="Snippets",icon="COLLAPSEMENU")
    self.layout.popover("TEXTSNIPPETSUILIST_PT_ListExample", text = "snippetsLIST", icon='VIEWZOOM')
    self.layout.separator()
    self.layout.popover("TEXT_PT_find", text = "検索", icon='EXPORT')
    self.layout.separator()
    self.layout.operator("text.class_viewer", text="Go to Last Error", icon="ERROR").cmd = "LAST_ERROR"
    self.layout.separator()
    self.layout.prop(context.scene.class_viewer, "line", text="       Jump to")#, icon="LINENUMBERS_ON")
    self.layout.prop(context.scene.class_viewer, "findtext", text="", icon="VIEWZOOM")

classes = [	TEXT_MT_def_viewer,
            TEXT_MT_class_viewer,
            TEXT_MT_comment_viewer,
            TEXT_MT_snippet_viewer,
            TEXT_OT_class_viewer,
            TEXT_OT_class_viewer_search,
            KSYNcontentsvieweraddonPreferences,
            # UI LISTのクラス
            TEXTSNIPPETSUILIST_ListItem,
            TEXTSNIPPETSUILISTmyuiPropertyGroup,
            TEXTSNIPPETSUILIST_PT_ListExample,
            TEXTSNIPPETSUILIST_OT_savefile,
            TEXTSNIPPETSUILIST_OT_loadfile,
            TEXTSNIPPETSUILIST_OT_get,
            TEXTSNIPPETSUILIST_OT_delete,
            TEXTSNIPPETSUILIST_OT_change,
            TEXTSNIPPETSUILIST_OT_NewItem,
            TEXTSNIPPETSUILIST_OT_MoveItem,
            TEXTSNIPPETSUILISTMY_UL_List,
            TEXTSNIPPETSUILIST_OT_openfile,


            ]

def register():

    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TEXT_MT_context_menu.append(draw_items)

    bpy.types.Scene.textsnippets_my_list = CollectionProperty(type = TEXTSNIPPETSUILIST_ListItem)
    bpy.types.Scene.textsnippets_list_index = IntProperty(name = "Index for textsnippets_my_list",
                                             default = 0,)
    bpy.types.Scene.textsnippets_uiprops = bpy.props.PointerProperty(type=TEXTSNIPPETSUILISTmyuiPropertyGroup)

def unregister():

    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.textsnippets_my_list
    del bpy.types.Scene.textsnippets_list_index
    del bpy.types.Scene.textsnippets_uiprops


if __name__ == "__main__":
    register()
