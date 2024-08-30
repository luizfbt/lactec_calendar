import flet as ft
import pdb
from datetime import date, datetime, timedelta
from pprintpp import pprint
from sqlalchemy.orm import Session
from typing import Any, List, Optional, Union, Callable

from db.models import *
from utils import utils
from utils.holidays import Holidays, CityType, months, weeks
import db.database as db


class Calendar(ft.Container):
    def __init__(self,
                 year: int,
                 month: int,
                 city_id: int,
                 has_adm_decisions: bool,
                 max_delta_years: int = 10):
        super().__init__()
        self.year = year
        self.month = month
        self.city_id = city_id
        self.has_adm_decisions = has_adm_decisions
        dt = datetime.now()
        self.this_year = dt.year
        self.last_year = -1
        self.last_city_id = -1
        self.max_delta_years = max_delta_years
        self.min_year = self.this_year - max_delta_years
        self.max_year = self.this_year + max_delta_years

        self.bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(color=ft.colors.ORANGE),
                        ft.Text("Carregando dados...")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                height=150
            )
        )
        
        self.nav_style = ft.TextStyle(
            size=20,
            weight=ft.FontWeight.BOLD
        )
        self.update_year_month(False)
        self.navigation = ft.Row(
            controls=[
                ft.IconButton(
                    ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                    on_click=self.on_previous_year,
                    tooltip="Ano anterior"
                ),
                ft.IconButton(
                    ft.icons.KEYBOARD_ARROW_LEFT,
                    on_click=self.on_previous_month,
                    tooltip="Mês anterior"
                ),
                self.year_month,
                ft.IconButton(
                    ft.icons.KEYBOARD_ARROW_RIGHT,
                    on_click=self.on_next_month,
                    tooltip="Próximo mês"
                ),
                ft.IconButton(
                    ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                    on_click=self.on_next_year,
                    tooltip="Próximo ano"
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        containers = []
        header_style = ft.TextStyle(
                size=20,
                weight=ft.FontWeight.BOLD
            )
        indexes = [6, 0, 1, 2, 3, 4, 5]
        for i in indexes:
            containers.append(ft.Container(
                content=ft.Text(weeks[i][:3].upper(),
                                color=ft.colors.TEAL_300,
                                style=header_style),
                bgcolor=ft.colors.BLACK,
                border_radius=10,
                border=ft.border.all(1, 'white'),
                alignment=ft.alignment.center)
            )

        self.gridview_header = ft.GridView(
            controls=containers,
            runs_count=7,
            padding=2,
            spacing=5,
            run_spacing=5,
            child_aspect_ratio=4.0,
        )

        self.gridview = ft.GridView(
            expand=True,
            runs_count=7,
            padding=2,
            spacing=5,
            run_spacing=5,
            auto_scroll=True,
            child_aspect_ratio=1.5
        )

        self.content = ft.Column(
            controls= [
                self.navigation,
                self.gridview_header,
                self.gridview
            ],
            spacing=1
        )


    def did_mount(self):
        # w = self.page.window.width - 100
        # if w < 1000:
        #     w = 1000
        # self.width = w

        self.update_content()


    def update_year_month(self, refresh: bool = False):
        self.year_month = ft.Text(
                f'{self.year} - {months[self.month - 1]}',
                style=self.nav_style,
                width=170)
        if refresh:
            self.content.controls[0].controls[2] = self.year_month


    def update_content(self):
        with db.session_scope() as session:
            dt = datetime(self.year, self.month, 1)
            sd = dt
            wd = dt.weekday()
            items = 42
            if wd < 6:
                days = wd + 1
                start_date = dt - timedelta(days=days)
            else:
                start_date = dt
            
            end_date = start_date + timedelta(days=items - 1)

            if self.last_year != self.year or self.last_city_id != self.city_id:
                self.last_year = self.year
                self.last_city_id = self.city_id

                new_year = db.get_first_year_holiday(session, self.year)
                if not new_year:
                    self.save_holidays_db(session)

            holidays = db.get_holidays(session,
                                       self.city_id,
                                       self.has_adm_decisions,
                                       start_date.date(),
                                       end_date.date())
            holidays_list = []
            for holiday in holidays:
                data_dict = {"date": holiday.date,
                             "reason": holiday.reason,
                             "type": holiday.type}
                holidays_list.append(data_dict)
            
            containers = []
            if wd < 6:
                days = wd + 1
                sd = dt - timedelta(days=days)
                for i in range(days):
                    container = self.day_container(sd.date(), holidays_list)
                    containers.append(container)
                    items -= 1
                    sd += timedelta(days=1)
            while items > 0:
                container = self.day_container(sd.date(), holidays_list)
                containers.append(container)
                items -= 1
                sd += timedelta(days=1)

            self.update_year_month(True)
            self.gridview.controls = containers
            self.update()


    def day_container(self,
                      date: date,
                      holidays_list: List[dict]) -> ft.Container:
        month = date.month
        weekday = date.weekday()
        items = utils.search_by_key(holidays_list, "date", date)
        is_holiday = len(items) > 0
        tooltip = items[0]['type'].value if is_holiday else None

        reason_style = ft.TextStyle(
            size=20,
            italic=True
        )

        if weekday >= 5: # Saturday or sunday
            text_color = ft.colors.WHITE
            bgcolor = ft.colors.GREY_600 \
                if month == self.month \
                else ft.colors.GREY_400
        else:
            if is_holiday:
                text_color = ft.colors.WHITE
                bgcolor = ft.colors.BLUE_ACCENT_400 \
                    if month == self.month \
                    else ft.colors.BLUE_ACCENT_100
            else:
                text_color = ft.colors.BLACK
                bgcolor = ft.colors.TEAL_50 \
                    if month == self.month \
                    else ft.colors.GREY_100

        if month == self.month:
            day_style = ft.TextStyle(
                size=20,
                weight=ft.FontWeight.BOLD
            )
        else:
            day_style = ft.TextStyle(
                size=20,
                weight=ft.FontWeight.NORMAL
            )
        
        if is_holiday:
            controls=[
                    ft.Text(date.day,
                            color=text_color,
                            style=day_style),
                    ft.Text(items[0]['reason'],
                            color=text_color,
                            style=reason_style)
            ]
        else:
            controls=[
                    ft.Text(date.day,
                            color=text_color,
                            style=day_style)
            ]
        container = ft.Container(
            content=ft.Column(controls=controls),
            bgcolor=bgcolor,
            border_radius=10,
            padding=ft.padding.all(10),
            border=ft.border.all(1, 'black'),
            tooltip=tooltip
        )
        return container

    
    def save_holidays_db(self, session: Session):
        self.page.open(self.bs)
        
        curitiba_holidays = Holidays(self.year, CityType.CURITIBA)
        salvador_holidays = Holidays(self.year, CityType.SALVADOR)
        navegantes_holidays = Holidays(self.year, CityType.NAVEGANTES, False)
        national_holidays_dict = curitiba_holidays.sorted_national
        curitiba_holidays_dict = curitiba_holidays.sorted_local
        salvador_holidays_dict = salvador_holidays.sorted_local
        navegantes_holidays_dict = navegantes_holidays.sorted_local
        
        self.save_holidays_dict_db(session,
                                   national_holidays_dict,
                                   0)
        
        if len(curitiba_holidays_dict) > 0:
            self.save_holidays_dict_db(session,
                                       curitiba_holidays_dict,
                                       1)
        
        if len(salvador_holidays_dict) > 0:
            self.save_holidays_dict_db(session,
                                       salvador_holidays_dict,
                                       2)
            
        if len(navegantes_holidays_dict) > 0:
            self.save_holidays_dict_db(session,
                                       navegantes_holidays_dict,
                                       3)

        self.page.close(self.bs)


    def save_holidays_dict_db(self, session: Session,
                              holidays_dict: List[dict],
                              group: int):
        db_holidays = []
        for dict in holidays_dict:
            date = dict['date']
            year_month = f'{date:%Y%m}'
            reason = dict['reason']
            type = dict['type']
            holiday = Holiday(
                date=date,
                year_month=year_month,
                reason=reason,
                type=type,
                group=group
            )
            db_holidays.append(holiday)
        
        if len(db_holidays) > 0:
            db.save_objects(session, db_holidays)


    def on_next_month(self, e: ft.ControlEvent):
        year = self.year
        month = self.month + 1
        if month > 12 and year < self.max_year:
            month = 1
            year += 1
        if year <= self.max_year:
            self.month = month
            self.year = year
            self.update_content()


    def on_previous_month(self, e: ft.ControlEvent):
        year = self.year
        month = self.month - 1
        if month < 1:
            month = 12
            year -= 1
        if year >= self.min_year:
            self.month = month
            self.year = year
            self.update_content()


    def on_next_year(self, e: ft.ControlEvent):
        year = self.year + 1
        if year <= self.max_year:
            self.year = year
            self.update_content()


    def on_previous_year(self, e: ft.ControlEvent):
        year = self.year - 1
        if year >= self.min_year:
            self.year = year
            self.update_content()


    def change_city(self, city_dict: dict):
        self.city_id = city_dict['id']
        self.has_adm_decisions = city_dict['has_adm_decisions']
        self.update_content()
