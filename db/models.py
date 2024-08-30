from db.connection import Base
from datetime import datetime, date
from sqlalchemy import Column, ForeignKey, Enum, Table
from sqlalchemy import Integer, String, Boolean, Date, DateTime, Float, Enum
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List, Literal
from typing import Optional
import enum


class HolidayType(enum.Enum):
    NATIONAL_HOLIDAY = 'Feriado nacional'
    LOCAL_HOLIDAY = 'Feriado local'
    MOBILE_HOLIDAY = 'Feriado móvel'
    ADMINISTRATIVE_DECISION = 'Decisão administrativa'


class LogType(enum.Enum):
    DEBUG = 'Debug'
    INFO = 'Info'
    ERROR = 'Error'
    WARNING = 'Warning'
    CRITICAL = 'Critical'


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    has_adm_decisions: Mapped[bool] = mapped_column(Boolean, default=True)


class Holiday(Base):
    __tablename__ = 'holiday'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date)
    year_month: Mapped[str] = mapped_column(String(6))
    reason: Mapped[str] = mapped_column(String(120))
    type: Mapped[HolidayType] = mapped_column(Enum(HolidayType))
    
    group: Mapped[int] = mapped_column(Integer)
    """Group: 0 - All cities, 1 - Curitiba, 2 - Salvador"""


class Config(Base):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(primary_key=True)
    dark_theme: Mapped[bool] = mapped_column(Boolean, default=False)
    window_width: Mapped[float] = mapped_column(Float, default=1600.0)
    window_height: Mapped[float] = mapped_column(Float, default=900.0)
    window_top: Mapped[float] = mapped_column(Float, default=10.0)
    window_left: Mapped[float] = mapped_column(Float, default=10.0)

    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"))


class Log(Base):
    __tablename__ = 'log'

    id: Mapped[int] = mapped_column(primary_key=True)
    """Log ID number, primary key."""

    date_hour: Mapped[datetime] = mapped_column(DateTime)
    """Log's date and time."""
    log_type: Mapped[LogType] = mapped_column(Enum(LogType))
    """The Log's message type: DEBUG, INFO, ERROR, WARNING, CRITICAL."""
    description: Mapped[str] = mapped_column(String(800))
    """Log's description."""
