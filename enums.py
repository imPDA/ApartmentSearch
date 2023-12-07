from enum import auto, StrEnum


class DealType(StrEnum):
    SALE = auto()  # продажа
    RENT = auto()  # аренда


class Category(StrEnum):
    LIVING = auto()  # жилая
    COMMERCIAL = auto()  # коммерческая
    GARAGE = auto()  # гараж


class OfferType(StrEnum):
    FLAT = auto()  # вторичка
    LAYOUT = auto()  # новостройка
    ROOM = auto()  # комната
    COMPLEX = auto()  # жилой комплекс
    HOUSE = auto()  # дом, дача
    HOUSE_PART = auto()  # часть дома
    TOWNHOUSE = auto()  # таунхаус
    LOT = auto()  # участок
    VILLAGE = auto()  # коттеджный, дачный посёлок


class Renovation(StrEnum):
    WITHOUT_REPAIR = auto()  # без ремонта
    STANDARD = auto()  # косметический
    WELL_DONE = auto()  # евроремонт
    DESIGN = auto()  # дизайнерский
