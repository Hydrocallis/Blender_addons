bl_info = {
    "version": (1, 6, 0),
    "blender": (3, 6, 5),
    "name": "KSYN File Back Up",
    "author": "Jonathan Stroem,KSYN",
    "description": "" ,
    "category": "3D",
    "location": "",
    }
import importlib
from pathlib import Path

#IMPORTS
import bpy, os
import shutil
from bpy.app.handlers import persistent
import datetime
from bpy.types import (
                        Panel,
                        Menu,
                        Operator,
                        PropertyGroup,
                        AddonPreferences,
                        )
from bpy.props import (
                        BoolProperty,
                        StringProperty,
                        IntProperty,
                        )


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

class KSYNfilebackupddonPreferences(AddonPreferences):

    bl_idname = __package__

    filepath: StringProperty(
        name="Example File Path",
        subtype='FILE_PATH',
    ) # type: ignore
    number: IntProperty(
        name="Example Number",
        default=4,
    )# type: ignore
    move_file_location: BoolProperty(
        name="Example Boolean",
        default=False,
    )# type: ignore

    back_up_script: BoolProperty(
        name=get_translang("Back up script","スクリプトをバックアップする"),
        default=True,
    )# type: ignore
    back_up_blenderfile: BoolProperty(
        name=get_translang("Back up blenderfile","ブレンダーファイルをバックアップする"),
        default=True,
    )# type: ignore

    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__].preferences
        layout.prop(addon_prefs, "move_file_location", text=get_translang("Move file location","場所を変える"))
        layout.prop(addon_prefs, "filepath", text=get_translang("File location","ファイルの場所"))
        layout.prop(addon_prefs, "back_up_blenderfile")
        layout.prop(addon_prefs, "back_up_script")

def backup_script():
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    # ファイルパスを取得
    filepath = bpy.data.filepath

    # ファイル名のみを取得
    filename = os.path.basename(filepath)

    # 拡張子を除去してブレンダーファイル名を取得
    blend_filename = os.path.splitext(filename)[0]+"_script"

    # 現在の時間を習得
    if not addon_prefs.move_file_location:
        file_direpath = os.path.dirname(bpy.data.filepath)
        
    else:
        file_direpath=addon_prefs.filepath
    now = datetime.datetime.now()
    date = str(now).split(' ')[0]
    time = (str(now).split(' ')[1]).split('.')[0]
    time3 = (str(time).split(':'))[0]
    time2 = (str(time).split(':'))[1]
    time = (str(time).split(':'))[2]
    # print(time)

    # 時間の変数を定義
    destination_day = date+"_"+time3+"_"+time2+"_"+time+"_"+"texts"
    
    # パスを作成
    destination_folder = os.path.join(file_direpath, blend_filename, destination_day)
    df = Path(destination_folder)

    #create if doesn't exist
    # フォルダのチェック　だと思う。
    if not df.exists():
        df.mkdir(parents=True, exist_ok=True)

    # 現在リンクしてるテキストを検査
    for text in bpy.data.texts:
        # テキスト名から拡張子を抽出
        _, extension = os.path.splitext(text.name)
        

        # テキスト名の文字数が22文字の場合
        if len(text.name) >= 19:
            # 省略されたテキスト名
            text.name = text.name[:8] + '...' + text.name[-7:]
            # print(f"省略されたテキスト名: {text.name}")
        else:
            # print(f"テキスト名: {text.name}")
            pass 
        # 拡張子が.py以外の場合の条件式
        if extension != '.py':
        # ここに条件がTrueの場合の処理を記述します
        # 例えば、拡張子が.py以外の場合に何かを行う場合はここにその処理を記述します
            text.name=text.name+".py"
            # print('###text.name',text.name)
        
        p = df / text.name
        script_path=text.as_string()

        p.write_text(script_path)
        # print(bpy.data.texts[0])        

def backup_blenderfile():
    filelocation = bpy.data.filepath
    addon_prefs = bpy.context.preferences.addons[__name__].preferences

    if not addon_prefs.move_file_location:
        backup_directory = os.path.join(os.path.dirname(filelocation),"backup.blend")
    else:
        backup_directory=addon_prefs.filepath

    file = {"fullpath": filelocation,
            "directory": os.path.dirname(filelocation),
            "name": bpy.path.display_name_from_filepath(filelocation),
            "extension": ".blend",
            "backup_amount": bpy.context.preferences.filepaths.save_version,
            "backup_directory": backup_directory
            }

    now = datetime.datetime.now()
    date = str(now).split(' ')[0]
    time = str(now).split(' ')[1].split('.')[0]
    time3 = str(time).split(':')[0]
    time2 = str(time).split(':')[1]
    time = str(time).split(':')[2]

    destination_folder = f"{date}_{time3}_{time2}_{time}_"
    file["time"] = destination_folder

    # バックアップディレクトリが存在しない場合は作成する
    backup_directory_path = os.path.join(file["backup_directory"])
    if not os.path.exists(backup_directory_path):
        os.makedirs(backup_directory_path)

    currentFiles = []
    for f in [f for f in os.listdir(backup_directory_path) for c in range(1, int(file["backup_amount"]) + 1)
            if f == file["name"] + file["extension"] + str(c) if os.path.isfile(os.path.join(backup_directory_path, f))]:
        currentFiles.append(f)

        name_ex_file_bk = file["time"] + file["name"] + file["extension"]

        print("#1 back up file is ", os.path.join(file["backup_directory"], name_ex_file_bk))
        os.rename(os.path.join(backup_directory_path, file["name"] + file["extension"] + "1"),
                os.path.join(backup_directory_path, name_ex_file_bk))

    if len(currentFiles) < 1:
        if os.path.isfile(file["fullpath"] + "1"):
            shutil.move(file["fullpath"] + "1",
                        os.path.join(file["backup_directory"], file["name"] + ".blend1"))

        print("back up move .blend1 file3")

@persistent
def move_handler(dummy):

    #fullpath = Full path to the data file.
    #directory = Directory the data file is in.
    #name = Name of file, without extension.
    #extension = Extension of files.
    #backup_amount = Max amount of backups to store.
    #backup_directory = The name of the backup directory. (Where the files should be moved.) So change this if you want to change where the backups are saved.
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    
    if addon_prefs.back_up_blenderfile:
        backup_blenderfile()    

    if addon_prefs.back_up_script:
        backup_script()
#This document is licensed according to GNU Global Public License v3.
classes = (
    move_handler,
    
    )


def register():
    
    for cls in classes:
        bpy.app.handlers.save_post.append(cls)
    bpy.utils.register_class(KSYNfilebackupddonPreferences)


KSYNfilebackupddonPreferences
def unregister():

    for cls in reversed(classes):
        bpy.app.handlers.save_post.remove(cls)
    bpy.utils.unregister_class(KSYNfilebackupddonPreferences)


if __name__ == "__main__":
    register()
