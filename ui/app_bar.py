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
        self.bgcolor=ft.Colors.WHITE10

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

        self.lactec_url = "https://lactec.com.br/"
        self.repository_url = "https://github.com/luizfbt/lactec_calendar"

        image = ft.Image(
            src=f"images/lacteclogo.png",
            width=20,
            height=20,
            fit="contain"
        )

        leading = ft.Container(
            ft.Row(
                [
                    image,
                    ft.Text("Lactec")
                ],
                spacing=5
            ),
            on_click=self.open_lactec_url
        )

        options = []
        current_city_name = None
        for city in cities:
            if city['id'] == self.city_id:
                current_city_name = city['name']
            options.append(
                ft.DropdownOption(
                    key=city['name'],
                    text=city['name']
                )
            )
        self.leading = leading
        dropdown = ft.Dropdown(
            options=options,
            width=250,
            value=current_city_name
        )
        dropdown.on_change = self.on_change_city
        self.title = dropdown
        self.center_title = True
        self.actions = [
            ft.IconButton(
                self.theme_icon(),
                on_click=self.change_theme
            ),
            ft.IconButton(
                ft.Icons.INFO,
                on_click=self.on_about
            ),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        'Repositório',
                        icon=ft.Icons.CODE_OUTLINED,
                        on_click=self.open_repository_url
                    ),
                    # ft.PopupMenuItem(
                    #     'Sair',
                    #     icon=ft.Icons.EXIT_TO_APP,
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
                on_tap_link=self.open_markdown_link,
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
        city_name = control.value
        for city in self.cities:
            if city['name'] == city_name:
                self.change_city(city)
                break


    def on_about(self, e: ft.ControlEvent):
        if self.dlg not in self.page.overlay:
            self.page.overlay.append(self.dlg)
        self.dlg.open = True
        self.page.update()


    def on_close_dlg(self, e: ft.ControlEvent):
        self.dlg.open = False
        self.page.update()


    async def open_lactec_url(self, _):
        await self.page.launch_url(self.lactec_url)


    async def open_repository_url(self, _):
        await self.page.launch_url(self.repository_url)


    async def open_markdown_link(self, e: ft.ControlEvent):
        await self.page.launch_url(e.data)
