"""
{
  "tender_number": "2110114712124000365",
  "tender_info_link": "some_link",
  "site_url": "https://zakupki.gov.ru",
  "customer": {
    "name": "Авиакомпания Северный ветер"
  },
  "contractor": {
    "name": "Авиакомпания Юг"
  },
  "date_start": "2025-01-15",
  "date_finish": "2025-02-15",
  "conditions": {
      "weather_conditions": [],
      "equipment_conditions": []
  },
  "additional_services": [],
  "contract_avia_datas": [
    {
      "arrival": {
        "name": "Москва",
        "longitude": "37.6173",
        "latitude": "55.7558"
      },
      "departure": {
        "name": "Санкт-Петербург",
        "longitude": "30.3609",
        "latitude": "59.9311"
      },
      "aircraft_examples": ["Ми-8", "Боинг 737"],
      "cargo": "Пассажиры",
      "cargo_volume": 100,
      "distance": 635,
      "flight_hours_number": 1,
      "aircraft_number": 2,
      "aircraft_type": "helicopter",
      "drone_type": "aerostatic",
      "drone_payload": 15,
      "drone_service_type": "service",
      "regularity_type": "regular",
      "work_type": "freight"
    }
  ]
}
"""


def build_json_for_avia_admin(contract_data: dict, avia_data: dict, contract_info) -> dict:
    """Сбор даты для вставки в таблицу авиаперевозок"""

    request = {
        "tender_number": contract_info.tender_number,
        "tender_info_link": contract_info.tender_info_link,
        "site_url": contract_info.site_url,
        "price": contract_info.price,
        "customer": { 
            "name": contract_info.customer,
        },
        "contractor": {"name": contract_data.get("contractor")} if contract_data.get("contractor") else None,
        "date_start": contract_data.get("date_start", None),
        "date_finish": contract_data.get("date_finish", None),
        "conditions": {
            "weather_conditions": contract_data.get("weather_conditions", None),
            "equipment_conditions": contract_data.get("equipment_conditions", None)
        },
        "additional_services": contract_data.get("additional_services", None),
        "contract_avia_datas": build_contract_avia_datas(avia_data)
    }
    return request

    
def build_contract_avia_datas(avia_data):
    datas = []
    for data in avia_data:
        datas.append({
            "aircraft_examples": data.get("aircraft_examples", None),
            "cargo": data.get("cargo", None),
            "cargo_volume": data.get("cargo_volume", None),
            "distance": data.get("distance", None),
            "flight_hours_number": data.get("flight_hours", None),
            "aircraft_number": data.get("aircraft_number", None),
            "drone_payload": data.get("drone_payload", None),
            "arrival": get_arrival(data),
            "departure": get_departure(data),
            "aircraft_type": convert_to_aircraft_type(data.get("aircraft_type", None)),
            "drone_type": convert_to_drone_type(data.get("drone_type", None)),
            "drone_service_type": convert_to_drone_service_type(data.get("drone_service_type", None)),
            "regularity_type": convert_to_regularity_type(data.get("regularity_type", None)),
            "work_type": convert_to_work_type(data.get("work_type", None)),
            "number_flies": convert_to_work_type(data.get("number_flies", None)),
        })
    return datas


def get_arrival(single_avia_data):
    if len(single_avia_data["route"]) == 0:
        return None
    
    return single_avia_data["route"][0]

def get_departure(single_avia_data):
    if len(single_avia_data["route"]) == 0:
        return None
    
    return single_avia_data["route"][-1]


def convert_to_aircraft_type(value):
    translation_dict = {
        "Вертолет": "helicopter",
        "Самолет": "plane",
        "Беспилотник": "drone",
    }
    return translation_dict.get(value, None)


def convert_to_drone_type(value):
    translation_dict = {
        "Аэростатические": "aerostatic",
        "Реактивные": "reactive",
        "Cамолётного типа": "fixed_wing",
        "Вертолётного типа": "rotary_wing",
        "Мультикоптерные": "multirotor",
        "Гибридные": "hybrid",
    }
    return translation_dict.get(value, None)


def convert_to_drone_service_type(value):
    translation_dict = {
        "Услуга": "service",
        "Покупка": "purchase",
    }
    return translation_dict.get(value, None)


def convert_to_regularity_type(value):
    translation_dict = {
        "Чартер": "charter",
        "Регулярный": "regular",
    }
    return translation_dict.get(value, None)


def convert_to_work_type(value):
    translation_dict = {
        "Грузоперевозки": "freight",
        "Пассажирские перевозки": "passenger",
        "Мониторинг": "monitoring",
        "Сельхоз работы": "agriculture",
        "Санитарный": "sanitary",
        "Пожарный": "fire_fighting",
    }
    return translation_dict.get(value, None)
