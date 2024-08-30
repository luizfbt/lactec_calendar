from utils.utils import root_path
import db.database as db
import flet as ft
import os


class AppBar(ft.AppBar):
    def __init__(self,
                 change_theme,
                 change_city,
                 exit_app,
                 theme_icon):
        super().__init__()
        self.change_theme = change_theme
        self.change_city = change_city
        self.exit_app = exit_app
        self.theme_icon = theme_icon
        self.bgcolor=ft.colors.SURFACE_VARIANT

        cities = []
        with db.session_scope() as session:
            config = db.get_config(session)
            self.city_id = config.city_id
            regs = db.get_cities(session)
            for reg in regs:
                cities.append({"id": reg.id,
                               "name": reg.name,
                               "has_adm_decisions": reg.has_adm_decisions})
        self.cities = cities

        lactec_url = "https://lactec.com.br/"
        repository_url = "https://github.com/luizfbt/lactec_calendar"
        
        image = ft.Image(
            src=f"images/lacteclogo.png",
            width=20,
            height=20,
            fit=ft.ImageFit.CONTAIN
        )
        
        leading = ft.Container(
            ft.Row(
                [
                    image,
                    ft.Text("Lactec")
                ],
                spacing=5
            ),
            on_click=lambda _: self.page.launch_url(lactec_url)
        )

        options = []
        dropdown_style = ft.TextStyle(
            size=20,
            weight=ft.FontWeight.BOLD
        )
        for i, city in enumerate(cities, 1):
            options.append(
                ft.dropdown.Option(key=i,
                                   text=city['name'],
                                   alignment=ft.alignment.center,
                                   text_style=dropdown_style)
            )
        self.leading = leading
        self.title = ft.Dropdown(
            icon=ft.icons.APPS,
            options=options,
            width=250,
            value=self.city_id,
            on_change=self.on_change_city
        )
        self.center_title = True
        self.actions = [
            ft.IconButton(
                self.theme_icon(),
                on_click=self.change_theme
            ),
            ft.IconButton(
                ft.icons.INFO,
                on_click=self.on_about
            ),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        'Repositório',
                        icon=ft.icons.CODE_OUTLINED,
                        on_click=lambda _: self.page.launch_url(repository_url)
                    ),
                    # ft.PopupMenuItem(
                    #     'Sair',
                    #     icon=ft.icons.EXIT_TO_APP,
                    #     on_click=self.exit_app
                    # ),
                ]
            )
        ]
    
        self.dlg = self.about_dialog()


    def about_dialog(self):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Sobre o Calendário Lactec",
                theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM
            )
        )
        
        about_file = os.path.join(root_path, 'about.md')
        if not os.path.exists(about_file):
            dlg.content = ft.Column(
                controls=[ft.Text('Arquivo "about.md" com as informações não encontrado!')],
                scroll=ft.ScrollMode.AUTO
            )
        else:
            with open(about_file, mode='r', encoding='utf-8') as file_ref:
                markdown = file_ref.read()
            
            md = ft.Markdown(
                value=markdown,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=lambda e: self.page.launch_url(e.data),
                code_theme='atom-one-light'
            )
            
            dlg.content = ft.Column(
                controls=[md],
                scroll=ft.ScrollMode.ADAPTIVE,
            )
            
        dlg.actions=[
            ft.TextButton("Fechar", on_click=self.on_close_dlg)
        ]
        return dlg


    def on_change_city(self, e: ft.ControlEvent):
        control: ft.Dropdown = e.control
        idx = int(control.value) - 1
        self.change_city(self.cities[idx])


    def on_about(self, e: ft.ControlEvent):
        self.page.open(self.dlg)


    def on_close_dlg(self, e: ft.ControlEvent):
        self.page.close(self.dlg)
