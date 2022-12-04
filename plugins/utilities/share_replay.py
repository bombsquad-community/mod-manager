# ba_meta require api 7
from __future__ import annotations
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from typing import Any, Sequence, Callable, List, Dict, Tuple, Optional, Union

from os import listdir, mkdir, path, sep
from shutil import copy, copytree

import ba
import _ba
from enum import Enum
from bastd.ui.tabs import TabRow
from bastd.ui.confirm import ConfirmWindow
from bastd.ui.watch import WatchWindow as ww
from bastd.ui.popup import PopupWindow

# mod by ʟօʊքɢǟʀօʊ
# export replays to mods folder and share with your friends or have a backup


def Print(*args, color=None, top=None):
    out = ""
    for arg in args:
        a = str(arg)
        out += a
    ba.screenmessage(out, color=color, top=top)


def cprint(*args):
    out = ""
    for arg in args:
        a = str(arg)
        out += a
    _ba.chatmessage(out)


title = "SHARE REPLAY"
internal_dir = _ba.get_replays_dir()+sep
external_dir = path.join(_ba.env()["python_directory_user"], "replays"+sep)

# colors
pink = (1, 0.2, 0.8)
green = (0.4, 1, 0.4)
red = (1, 0, 0)
blue = (0.26, 0.65, 0.94)
blue_highlight = (0.4, 0.7, 1)

if not path.exists(external_dir):
    mkdir(external_dir)
    Print("You are ready to share replays", color=pink)


class Help(PopupWindow):
    def __init__(self):
        uiscale = ba.app.ui.uiscale
        self.width = 1000
        self.height = 300

        PopupWindow.__init__(self,
                             position=(0.0, 0.0),
                             size=(self.width, self.height),
                             scale=1.2,)

        ba.containerwidget(edit=self.root_widget, on_outside_click_call=self.close)
        ba.textwidget(parent=self.root_widget, position=(0, self.height * 0.6),
                      text=f">Replays are exported to\n     {external_dir}\n>Copy replays to the above folder to be able to import them into the game\n>I would live to hear from you,meet me on discord\n                                -LoupGarou(author)")

    def close(self):
        ba.playsound(ba.getsound('swish'))
        ba.containerwidget(edit=self.root_widget, transition="out_right",)


class SettingWindow():
    def __init__(self):
        self.draw_ui()
        ba.containerwidget(edit=self.root, cancel_button=self.close_button)
        self.selected_name = None
        # setting tab when window opens
        self.on_tab_select(self.TabId.INTERNAL)
        self.tab_id = self.TabId.INTERNAL

    class TabId(Enum):
        INTERNAL = "internal"
        EXTERNAL = "external"

    def sync_confirmation(self):
        ConfirmWindow(text="WARNING:\nreplays with same name in mods folder\n will be overwritten",
                      action=self.sync, cancel_is_selected=True)

    def on_select_text(self, widget, name):
        existing_widgets = self.scroll2.get_children()
        for i in existing_widgets:
            ba.textwidget(edit=i, color=(1, 1, 1))
        ba.textwidget(edit=widget, color=(1, 1, 0))
        self.selected_name = name

    def on_tab_select(self, tab_id):
        self.tab_id = tab_id
        if tab_id == self.TabId.INTERNAL:
            dir_list = listdir(internal_dir)
            ba.buttonwidget(edit=self.share_button, label="EXPORT", icon=ba.gettexture("upButton"),)
        else:
            dir_list = listdir(external_dir)
            ba.buttonwidget(edit=self.share_button, label="IMPORT",
                            icon=ba.gettexture("downButton"),)
        self.tab_row.update_appearance(tab_id)
        dir_list = sorted(dir_list)
        existing_widgets = self.scroll2.get_children()
        if existing_widgets:
            for i in existing_widgets:
                i.delete()
        height = 900
        # making textwidgets for all replays
        for i in dir_list:
            height -= 40
            a = i
            i = ba.textwidget(
                parent=self.scroll2,
                size=(500, 50),
                text=i.split(".")[0],
                position=(10, height),
                selectable=True,
                max_chars=40,
                corner_scale=1.3,
                click_activate=True,)
            ba.textwidget(edit=i, on_activate_call=ba.Call(self.on_select_text, i, a))

    def draw_ui(self):
        self.uiscale = ba.app.ui.uiscale
        self.root = ba.Window(ba.containerwidget(
            size=(900, 670), on_outside_click_call=self.close, transition="in_right")).get_root_widget()

        self.close_button = ba.buttonwidget(
            parent=self.root,
            position=(90, 560),
            button_type='backSmall',
            size=(60, 60),
            label=ba.charstr(ba.SpecialChar.BACK),
            scale=1.5,
            on_activate_call=self.close)

        ba.textwidget(
            parent=self.root,
            size=(200, 100),
            position=(350, 550),
            scale=2,
            selectable=False,
            h_align="center",
            v_align="center",
            text=title,
            color=green)

        ba.buttonwidget(
            parent=self.root,
            position=(650, 580),
            size=(35, 35),
            texture=ba.gettexture("achievementEmpty"),
            label="",
            on_activate_call=Help)

        tabdefs = [(self.TabId.INTERNAL, 'INTERNAL'), (self.TabId.EXTERNAL, "EXTERNAL")]
        self.tab_row = TabRow(self.root, tabdefs, pos=(150, 500-5),
                              size=(500, 300), on_select_call=self.on_tab_select)

        self.share_button = ba.buttonwidget(
            parent=self.root,
            position=(720, 400),
            size=(110, 50),
            scale=1.5,
            button_type="square",
            label="EXPORT",
            text_scale=2,
            icon=ba.gettexture("upButton"),
            on_activate_call=self.share)

        sync_button = ba.buttonwidget(
            parent=self.root,
            position=(720, 300),
            size=(110, 50),
            scale=1.5,
            button_type="square",
            label="SYNC",
            text_scale=2,
            icon=ba.gettexture("ouyaYButton"),
            on_activate_call=self.sync_confirmation)

        scroll = ba.scrollwidget(
            parent=self.root,
            size=(600, 400),
            position=(100, 100),)
        self.scroll2 = ba.columnwidget(parent=scroll, size=(
            500, 900))

    def share(self):
        if self.selected_name is None:
            Print("Select a replay", color=red)
            return
        if self.tab_id == self.TabId.INTERNAL:
            self.export()
        else:
            self.importx()

        # image={"texture":ba.gettexture("bombColor"),"tint_texture":None,"tint_color":None,"tint2_color":None})

    def sync(self):
        internal_list = listdir(internal_dir)
        external_list = listdir(external_dir)
        for i in internal_list:
            copy(internal_dir+sep+i, external_dir+sep+i)
        for i in external_list:
            if i in internal_list:
                pass
            else:
                copy(external_dir+sep+i, internal_dir+sep+i)
        Print("Synced all replays", color=pink)

    def export(self):
        copy(internal_dir+self.selected_name, external_dir+self.selected_name)
        Print(self.selected_name[0:-4]+" exported", top=True, color=pink)

    def importx(self):
        copy(external_dir+self.selected_name, internal_dir+self.selected_name)
        Print(self.selected_name[0:-4]+" imported", top=True, color=green)

    def close(self):
        ba.playsound(ba.getsound('swish'))
        ba.containerwidget(edit=self.root, transition="out_right",)


# ++++++++++++++++for keyboard navigation++++++++++++++++

        #ba.widget(edit=self.enable_button, up_widget=decrease_button, down_widget=self.lower_text,left_widget=save_button, right_widget=save_button)

# --------------------------------------------------------------------------------------------------

ww.__old_init__ = ww.__init__


def new_init(self, transition="in_right", origin_widget=None):
    self.__old_init__(transition, origin_widget)
    self._share_button = ba.buttonwidget(
        parent=self._root_widget,
        position=(self._width*0.70, self._height*0.80),
        size=(220, 60),
        scale=1.0,
        color=green,
        icon=ba.gettexture('usersButton'),
        iconscale=1.5,
        label=title,
        on_activate_call=SettingWindow)


# ba_meta export plugin

class Loup(ba.Plugin):
    def on_app_running(self):
        ww.__init__ = new_init

    def has_settings_ui(self):
        return True

    def show_settings_ui(self, button):
        SettingWindow()

    def on_plugin_manager_prompt(self):
        SettingWindow()
