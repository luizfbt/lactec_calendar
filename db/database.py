from contextlib import contextmanager
from datetime import date, datetime
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session
from typing import Any, List, Optional, Union, Callable

import pandas as pd
import pdb

from db.connection import SessionLocal
from db.models import *
from utils import utils


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        # session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_cities(session: Session) -> List[City]:
    try:
        regs = session.query(City).order_by(City.id).all()
        if len(regs) == 0:
            city1 = City(name='Curitiba/PR')
            city2 = City(name='Salvador/BA')
            city3 = City(name='Navegantes/SC',
                         has_adm_decisions=False)
            save_object(session, city1)
            save_object(session, city2)
            save_object(session, city3)
            return [city1, city2, city3]
        
        return regs

    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def get_city_by_id(session: Session, city_id: int) -> City:
    try:
        reg = session.query(City).filter(City.id == city_id).first()
        return reg

    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def get_first_year_holiday(session: Session,
                           year: int) -> Holiday:
    try:
        dt = date(year, 1, 1)
        reg = session.query(Holiday).filter(and_(\
            Holiday.group == 0,
            Holiday.date == dt)).first()
        return reg

    except Exception as e:
        save_log_message(session, LogType.ERROR, e)
    

def get_month_holidays(session: Session,
                       city_id: int,
                       year_month: str) -> List[Holiday]:
    try:
        regs = session.query(Holiday).filter(and_(\
            Holiday.city_id == city_id,
            Holiday.year_month == year_month)).\
            order_by(Holiday.date).all()
        return regs

    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def get_holidays(session: Session,
                 group: int,
                 has_adm_decisions: bool,
                 start_date: date,
                 end_date: date):
    try:
        if group == 0:
            groups = [0]
        else:
            groups = [0, group]

        if has_adm_decisions:
            regs = session.query(Holiday).filter(and_(\
                Holiday.group.in_(groups),
                Holiday.date.between(start_date, end_date))).\
                order_by(Holiday.date).all()
        else:
            regs = session.query(Holiday).filter(and_(\
                Holiday.group.in_(groups),
                Holiday.type != HolidayType.ADMINISTRATIVE_DECISION,
                Holiday.date.between(start_date, end_date))).\
                order_by(Holiday.date).all()
        return regs

    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def get_config(session: Session) -> Config:
    try:
        reg = session.query(Config).first()
        if reg is None:
            cities = get_cities(session)
            reg = Config(dark_theme=False,
                         window_width=1292.0,
                         window_height=930.0,
                         window_top=10.0,
                         window_left=10.0,
                         city_id=cities[0].id)
            save_object(session, reg)
        return reg
    
    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def set_theme(session: Session,
              dark_theme: bool):
    try:
        reg = get_config(session)
        reg.dark_theme = dark_theme
        save_object(session, reg)
    
    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def set_city_id(session: Session,
              city_id: int):
    try:
        reg = get_config(session)
        reg.city_id = city_id
        save_object(session, reg)
    
    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def set_page_window(session: Session,
                    width: float,
                    height: float,
                    top: float,
                    left: float):
    try:
        reg = get_config(session)
        reg.window_width = width
        reg.window_height = height
        reg.window_top = top
        reg.window_left = left
        save_object(session, reg)
    
    except Exception as e:
        save_log_message(session, LogType.ERROR, e)


def save_object(session: Session, obj):
    try:
        session.add(obj)
        session.commit()
    
    except Exception as e:
        session.rollback()
        save_log_message(session, LogType.ERROR, e)


def save_objects(session: Session, object_list):
    try:
        session.bulk_save_objects(object_list)
        session.commit()
    
    except Exception as e:
        session.rollback()
        save_log_message(session, LogType.ERROR, e)


def save_log_message(session: Session, 
                     log_type: LogType, 
                     e: Exception):
    """Save the log message on the database.

    Args:
        log_type (str): Log message type: DEBUG, INFO, ERROR, WARNING, CRITICAL.
        description (str): The log message.
    """
    try:
        description = utils.error_handling(e)
        datetime_now = datetime.now() # + timedelta(seconds=cfg.app.time_shift)
        log = Log(date_hour=datetime_now,
                  log_type=log_type,
                  description=description)
        save_object(session, log)

    except Exception as e:
        print(f'Erro ao salvar o log: {e}')
