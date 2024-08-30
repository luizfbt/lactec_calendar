from utils.holidays import Holidays, CityType
from ui.app import *

import flet as ft
import locale
import pandas as pd


def test():
    for year in range(2024, 2025):
        holidays = Holidays(year, city_type=CityType.SALVADOR)
        df = pd.DataFrame(data=holidays.sorted_national)
        df2 = pd.DataFrame(data=holidays.sorted_local)
        print(df)
        print("_" * 50)
        print(df2)
        print("_" * 50)


if __name__ == '__main__':
    # test()
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    ft.app(App, assets_dir="assets", port=8080, view=ft.AppView.FLET_APP_WEB)
