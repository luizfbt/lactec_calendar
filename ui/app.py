import flet as ft
import os
import pdb
from datetime import datetime

from ui.calendar import Calendar
from ui.app_bar import AppBar
import db.connection as dbconn
import db.database as db
import db.models as models

models.Base.metadata.create_all(bind=dbconn.engine)


class App:
    def __init__(self, page: ft.Page):

        self.page = page
        self.page.theme = ft.Theme(color_scheme_seed='green')
        self.page.on_resized = self.page_resize
        self.page.scroll = ft.ScrollMode.AUTO

        self.page.title = "Calendário Lactec"
        
        with db.session_scope() as session:
            config = db.get_config(session)

            self.city_id = config.city_id
            city = db.get_city_by_id(session, self.city_id)
            self.has_adm_decisions = city.has_adm_decisions

            if config.dark_theme:
                self.page.theme_mode = ft.ThemeMode.DARK
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT

            self.page.window.width = config.window_width
            self.page.window.height = config.window_height
            self.page.window.top = config.window_top
            self.page.window.left = config.window_left

        self.main_page()


    def page_resize(self, e):
        with db.session_scope() as session:
            db.set_page_window(session,
                               self.page.window.width,
                               self.page.window.height,
                               self.page.window.top,
                               self.page.window.left)


    def theme_icon(self):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.icons.LIGHT_MODE
        return ft.icons.DARK_MODE


    def change_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            dark_theme = False
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            dark_theme = True
        e.control.icon = self.theme_icon()
        self.page.update()
        
        with db.session_scope() as session:
            db.set_theme(session, dark_theme)


    def change_city(self, city_dict: dict):
        self.city_id = city_dict['id']
        self.calendar.change_city(city_dict)

        with db.session_scope() as session:
            db.set_city_id(session, self.city_id)


    def exit_app(self, e):
        self.page.window.close()


    def main_page(self):
        self.page.appbar = AppBar(
            self.change_theme,
            self.change_city,
            self.exit_app,
            self.theme_icon)

        dt = datetime.now()

        self.calendar = Calendar(dt.year,
                                 dt.month,
                                 self.city_id,
                                 self.has_adm_decisions)
        
        self.page.add(self.calendar)
