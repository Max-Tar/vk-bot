# -*- coding: utf-8 -*-
from pony.orm import Database, Required, Json
from config_db import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария"""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """Заявка на регистрацию"""
    city_departure = Required(str)
    city_arrival = Required(str)
    user_flight_date = Required(str)
    user_flight = Required(str)
    seat = Required(str)
    comment = Required(str)
    telephone = Required(str)


db.generate_mapping(create_tables=True)
