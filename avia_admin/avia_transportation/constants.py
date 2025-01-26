from django.db.models import TextChoices


class AirCraftType(TextChoices):
    HELICOPTER = "helicopter", "Вертолет"
    PLANE = "plane", "Самолет"
    DRONE = "drone", "Беспилотник"


class DroneType(TextChoices):
    AEROSTATIC = "aerostatic", "Аэростатические БПЛА"
    REACTIVE = "reactive", "Реактивные БПЛА"
    FIXED_WING = "fixed_wing", "БПЛА самолётного типа"
    ROTARY_WING = "rotary_wing", "БПЛА вертолётного типа"
    MULTIROTOR = "multirotor", "Мультикоптерные (мультироторные) БПЛА"
    HYBRID = "hybrid", "Гибридные БПЛА"


class DroneServiceType(TextChoices):
    SERVICE = "service", "Услуга"
    PURCHASE = "purchase", "Покупка"


class ContractRegularityType(TextChoices):
    REGULAR = "regular", "Регулярный"
    CHARTER = "charter", "Чартер"


class WorkType(TextChoices):
    FREIGHT = 'freight', 'Грузоперевозки'
    PASSENGER = 'passenger', 'Пассажирские перевозки'
    MONITORING = 'monitoring', 'Мониторинг'
    AGRICULTURE = 'agriculture', 'Сельхоз работы'
    SANITARY = 'sanitary', 'Санитарный'
    FIRE_FIGHTING = 'fire_fighting', 'Пожарный'


class ContactType(TextChoices):
    REGULAR = "purchase", "Закупки"
    CHARTER = "contract", "Контракт"


