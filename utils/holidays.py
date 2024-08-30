from datetime import date, datetime, timedelta
from collections import OrderedDict
from enum import Enum
from typing import Any, List, Optional, Union, Callable
import pandas as pd
import pdb

from db.models import HolidayType


# Referências:
# https://pipeless.blogspot.com/2008/10/calculando-data-da-pscoa-em-python.html
# https://www.curitiba.pr.gov.br/conteudo/feriados-municipais-de-curitiba/210

# Define os nomes dos meses e semanas como estão no pdf
months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
weeks = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']


class CityType(Enum):
    CURITIBA = 1
    SALVADOR = 2
    NAVEGANTES = 3


# Adapted from: https://astroparsec.com/es/2021/04/02/a-pascoa-e-a-lua
def calc_easter(year):
    """Calculate the date of Easter according to the year.

    Arguments:
        year (int): Year of Easter.

    Returns:
        date: The date of Easter.
    """
    y = year
    g = y % 19 + 1 # Aureal Number
    c = y // 100 + 1
    x = 3 * c // 4 - 12
    z = (8 * c + 5) // 25 - 5
    d = 5 * y // 4 - x - 10
    e = (11 * g + 20 + z - x) % 30

    # Epacta
    if ((e == 25) & (g > 11)) | (e == 24):
        e += 1

    # Meton Cycle
    n = 44 - e
    if (n < 21):
        n += 30
    n = n + 7 - (d + n) % 7
    m=3
    if (n>31):
        n-=31
        m = 4

    return date(y, m, n)


class Holidays:
    """Class that returns a list of public holiday data (holidays), including administrative decisions.

    Arguments:
        year (int): The reference year.
        type_city (:obj:`TypeCity`): The type of the city: City.CURITIBA or City.SALVADOR.
    """
    def __init__(self,
                 year: int = datetime.now().year,
                 city_type: CityType = CityType.CURITIBA,
                 has_adm_decisions: bool = True):
        self.year = year
        self.city_type = city_type
        self.holidays = []
        self.init_fixed_holidays()
        self.init_mobile_holidays()
        if city_type == CityType.CURITIBA:
            self.init_curitiba_holidays()
        elif city_type == CityType.SALVADOR:
            self.init_salvador_holidays()
        else:
            self.init_navegantes_holidays()
        
        if has_adm_decisions:
            self.init_administrative_decisions()

    
    def add_holiday(self, date: date,
                    reason: str,
                    type: HolidayType,
                    is_local: bool = False):
        """Adds a new datum to the list of holidays.

        Arguments:
            date (date): Date.
            reason (str): Reason for the holiday.
            type (str): Type: national holiday, local holiday or administrative decision.
            is_local (bool): `True` if holiday is city's only.
        """
        global weeks

        week_day = weeks[date.weekday()]

        dicio = {"date": date,
                 "Day": week_day,
                 "reason": reason,
                 "type": type,
                 "is_local": is_local}
        self.holidays.append(dicio)

    
    def init_fixed_holidays(self):
        """Initializes Brazil's national holidays.
        """
        type = HolidayType.NATIONAL_HOLIDAY
        self.add_holiday(date(self.year, 1, 1), "Ano Novo", type)
        self.add_holiday(date(self.year, 4, 21), "Tiradentes", type)
        self.add_holiday(date(self.year, 5, 1), "Dia do Trabalhador", type)
        self.add_holiday(date(self.year, 9, 7), "Independência do Brasil", type)
        self.add_holiday(date(self.year, 10, 12), "Nossa Senhora Aparecida", type)
        self.add_holiday(date(self.year, 11, 2), "Finados", type)
        self.add_holiday(date(self.year, 11, 15), "Proclamação da República", type)
        if self.year >= 2024:
            self.add_holiday(date(self.year, 11, 20),
                             "Dia Nacional de Zumbi e da Consciência Negra",
                             type)
        self.add_holiday(date(self.year, 12, 25), "Natal", type)


    def add_date_days(self, data:date, dias:int):
        """Adds days to a specific date.

        Arguments:
            date (date): Date to add the days to.
            days (int): Days to be added to the date.

        Returns:
            date: Result of the new date.
        """
        dt = datetime.combine(data, datetime.min.time())
        new_date = dt + timedelta(days=dias)
        return new_date.date()


    def init_mobile_holidays(self):
        """Calculates mobile holidays.
        """
        type = HolidayType.MOBILE_HOLIDAY
        easter = calc_easter(self.year)
        self.add_holiday(easter, "Páscoa", type)
        self.add_holiday(self.add_date_days(easter, -48),
                         "Carnaval",
                         HolidayType.ADMINISTRATIVE_DECISION)
        self.add_holiday(self.add_date_days(easter, -47),
                         "Carnaval",
                         type)
        self.add_holiday(self.add_date_days(easter, -46),
                         "Cinzas",
                         HolidayType.ADMINISTRATIVE_DECISION)
        self.add_holiday(self.add_date_days(easter, -2),
                         "Paixão de Cristo",
                         type)
        self.add_holiday(self.add_date_days(easter, 60),
                         "Corpus Christi",
                         type)


    def init_curitiba_holidays(self):
        """Adds the dates of local holidays in Curitiba/PR.
        """
        self.add_holiday(date(self.year, 9, 8),
                         "Nossa Senhora da Luz dos Pinhais",
                         HolidayType.LOCAL_HOLIDAY,
                         True)

    
    def init_salvador_holidays(self):
        """Adds the dates of local holidays in Salvador/BA.
        """
        type = HolidayType.LOCAL_HOLIDAY
        self.add_holiday(date(self.year, 6, 24), "São João", type, True)
        self.add_holiday(date(self.year, 7, 2), "Independência da Bahia", type, True)
        self.add_holiday(date(self.year, 12, 8), "Nossa Senhora da Conceição", type, True)

    
    def init_navegantes_holidays(self):
        """Adds the dates of local holidays in Navegantes/SC"""
        type = HolidayType.LOCAL_HOLIDAY
        self.add_holiday(date(self.year, 2, 2), "Nossa Senhora dos Navegantes", type, True)
        self.add_holiday(date(self.year, 8, 26), "Aniversário de Navegantes", type, True)


    def holiday_days_diff_date(self, reason: str, days: int=0):
        """Returns the date of the holiday with offset days.

        Arguments:
            reason (str): Reason of the holiday to be searched.
            days (int, optional): Adds days to the date of the holiday: can be a negative or positive value. The default is 0.

        Returns:
            Date: Date with offset.
        """
        dict_data = next((item for item in self.holidays if item['reason'] == reason), None)
        if dict_data:
            if days:
                return dict_data['date'] + timedelta(days=days)
            
            return dict_data['date']


    def holiday_dict_by_date(self, date: date):
        """Returns the data dictionary for a specific date.

        Arguments:
            date (date): Date to search for the day in the list of holiday dictionaries.

        Returns:
            dict list: List of holiday dictionaries for the day.
        """
        dict_list = list(item for item in self.holidays if item['date'] == date)
        return dict_list


    def add_bridge_day(self, reason: str, type: HolidayType, is_local: bool):
        """Adds the bridge day to the list of public holidays.

        Arguments:
            reason (str): Reason for the holiday to be searched.
            type (str): Type: national holiday, local holiday or administrative decision.
        """
        days_list = [-1, 1]
        for days in days_list:
            date = self.holiday_days_diff_date(reason, days)
            holiday_date = self.holiday_dict_by_date(date)
            if date and date.weekday() in [0, 4] and not holiday_date:
                self.add_holiday(date, "Dia ponte", type, is_local)
                break
    

    def init_administrative_decisions(self):
        """Adds administrative decisions to the list of public holidays.
        """
        type = HolidayType.ADMINISTRATIVE_DECISION

        christmas_eve = datetime(self.year, 12, 24).date()
        # if christmas_eve.weekday() in [0, 4]:
        self.add_holiday(christmas_eve, "Véspera de Natal", type)

        new_years_eve = datetime(self.year, 12, 31).date()
        # if new_years_eve.weekday() == 4:
        self.add_holiday(new_years_eve, "Véspera de Ano Novo", type)

        reasons_excl = ["Ano Novo", 
                        "Natal", 
                        "Carnaval", 
                        "Cinzas", 
                        "Paixão de Cristo"]
        
        for holiday in self.holidays:
            if holiday['type'] == type:
                continue # if the public holiday type is Administrative Decision, it does not generate another bridge day.

            if holiday['date'].weekday() > 4:
                continue # if the day is saturday or sunday, the next holiday, as there will be no bridge day.

            reason = holiday['reason']
            is_local = holiday['is_local']
            if reason not in reasons_excl:
                self.add_bridge_day(reason, type, is_local)


    @property
    def sorted(self) -> List[dict]:
        """Property that returns all sorted dates.

        Return:
            dict list: Dictionary list of holidays.
        """
        my_time = datetime.min.time()
        items = sorted(self.holidays, \
            key = lambda i: (datetime.combine(i["date"], my_time)))
        return items
    
    @property
    def sorted_local(self) -> List[dict]:
        """Property that returns all local sorted dates.

        Return:
            dict list: Dictionary list of holidays.
        """
        items = self.sorted
        local_items = [item for item in items if item['is_local']]
        return local_items


    @property
    def sorted_national(self) -> List[dict]:
        """Property that returns all local sorted dates.

        Return:
            dict list: Dictionary list of holidays.
        """
        items = self.sorted
        national_items = [item for item in items if not item['is_local']]
        return national_items


def test():
    # Teste da classe Feriados:
    #   - Imprimir os feriados de 2016 a 2022. 
    for year in range(2024, 2025):
        holidays = Holidays(year)
        dates = holidays.sorted_national
        df = pd.DataFrame(data=holidays.sorted_national)
        df2 = pd.DataFrame(data=holidays.sorted_local)
        print(df)
        print("_" * 50)
        print(df2)
        print("_" * 50)
