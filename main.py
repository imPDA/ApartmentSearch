import asyncio
import math
import urllib.parse
from pprint import pprint
from typing import List, Callable, Any

import folium
from folium import DivIcon

from cian_datatypes import CianOffer
from clients.domclick import DomclickClient
from datatypes import SearchParameters, DomclickOffer
from domclick_datatypes import Offer, DomclickOffer_v2


def eliminate_list(input_: dict) -> dict:
    output_ = {}

    for k, v in input_.items():
        if len(v) == 1:
            output_.update({k: v[0]})
        else:
            output_.update({k: v})

    return output_


def parse_url(raw_url: str) -> SearchParameters:
    parsed_url = urllib.parse.urlparse(raw_url)
    parsed_qs = urllib.parse.parse_qs(parsed_url.query)
    parsed_qs = eliminate_list(parsed_qs)

    return SearchParameters(**parsed_qs)


# '3849dc90-7f7b-4285-b4ca-4ac2b8fa6e51' Тамбов
# 'abf4ae61-af59-4b2d-a8d9-fdf9b47c4a5d' Киров
# '7b4698a7-f8b8-424c-9195-e24f3ddb88f3' Питер

async def get_some_offers():
    client = DomclickClient()

    my_search = SearchParameters(
        address='abf4ae61-af59-4b2d-a8d9-fdf9b47c4a5d',
        deal_type='sale',
        category='living',
        offer_type=['layout'],  # 'flat',
        price=(None, 5_000_000),
        area=(30, None),
        # has_separated_bathrooms=True,
        # renovation=('well_done', 'design'),
        # has_lifts=True
    )

    return await client.get_all_offers(my_search)


def calculate_radius_linear(sum: float, price_range: tuple[float, float], map_to: tuple[float, float]) -> float:
    k = (map_to[1] - map_to[0]) / (price_range[1] - price_range[0])
    b = map_to[0] - k * price_range[0]

    return k * sum + b


def calculate_radius_exponential(price: float, price_range: tuple[float, float], map_to: tuple[float, float]) -> float:
    k = (math.log(map_to[1] / map_to[0])) / (price_range[1] - price_range[0])
    b = math.log(map_to[0]) - k * price_range[0]

    return math.exp(k * price + b)


def calculate_radius_logarithmic(price: float, price_range: tuple[float, float], map_to: tuple[float, float]) -> float:
    k = (math.exp(map_to[1] / 10) - math.exp(map_to[0] / 10)) / (price_range[1] - price_range[0])
    b = math.exp(map_to[0] / 10) - k * price_range[0]

    return math.log(k * price + b) * 10


def calculate_radius_root(price: float, price_range: tuple[float, float], map_to: tuple[float, float]) -> float:
    if price_range[1] == price_range[0]:
        return map_to[1]

    k = (math.pow(map_to[1], 2) - math.pow(map_to[0], 2)) / (price_range[1] - price_range[0])
    b = math.pow(map_to[0], 2) - k * price_range[0]

    return math.sqrt(k * price + b)


def get_location(offer: DomclickOffer | CianOffer) -> tuple[float, float]:
    if isinstance(offer, DomclickOffer):
        return offer.address.position.lat, offer.address.position.lon

    if isinstance(offer, DomclickOffer_v2):
        return offer.location.lat, offer.location.lon

    raise NotImplementedError()


def get_popup_info(offer: DomclickOffer | CianOffer) -> str:
    if isinstance(offer, DomclickOffer):
        info = list([offer.address.display_name, ])
        info.append(f"{offer.price_info.price / 1_000_000:,.2f}M RUB ({get_square_price(offer):,.0f} RUB/m2)")
        info.append(f"{offer.object_info.area:.1f} m2 ({offer.object_info.rooms} room(s))")

        return '<br><br>'.join(info)

    if isinstance(offer, DomclickOffer_v2):
        link = f'<a href="{offer.path}">{offer.address.displayName}</a>'
        info = list([link, ])
        info.append(f"{get_price(offer) / 1_000_000:,.2f}M RUB ({get_square_price(offer):,.0f} RUB/m2)")
        info.append(f"{offer.generalInfo.area:.1f} m2 ({offer.generalInfo.rooms} room(s))")

        return '<br><br>'.join(info)

    raise NotImplementedError()


def func(offer: DomclickOffer | CianOffer) -> float:
    if isinstance(offer, DomclickOffer):
        return offer.price_info.price

    raise NotImplementedError()


def get_square_price(offer: Offer) -> float:
    if isinstance(offer, DomclickOffer):
        return offer.price_info.square_price

    if isinstance(offer, DomclickOffer_v2):
        return offer.price / offer.generalInfo.area

    raise NotImplementedError()


def get_price(offer: Offer) -> float:
    if isinstance(offer, DomclickOffer):
        return offer.price_info.price

    if isinstance(offer, DomclickOffer_v2):
        return offer.price

    raise NotImplementedError()


def get_range(objects: List[Any], *, key: Callable = lambda x: x) -> tuple[float, float]:
    if not objects:
        raise ValueError("Empty list")

    values = tuple(map(key, objects))
    return min(values), max(values)


def get_area(offer: Offer) -> float:
    if isinstance(offer, DomclickOffer):
        return offer.object_info.area

    if isinstance(offer, DomclickOffer_v2):
        return offer.generalInfo.area

    raise NotImplementedError()


if __name__ == '__main__':
    m = folium.Map(location=(58.6072106, 49.6223879), zoom_start=12)

    offers = asyncio.run(get_some_offers())
    offers.sort(key=lambda x: -get_square_price(x))

    for offer in offers:
        location = get_location(offer)

        iframe = folium.IFrame()
        popup = folium.Popup(get_popup_info(offer), max_width=200)

        folium.Circle(
            radius=calculate_radius_root(get_square_price(offer), get_range(offers, key=get_square_price), (10.0, 150.0)),
            location=location,
            popup=popup,
            color="#C30010",
            stroke=True,
            fill=True
        ).add_to(m)

        folium.map.Marker(
            location=location,
            icon=DivIcon(html=f'<div style="font-size: 8pt">{get_area(offer):.0f}</div>')
        ).add_to(m)

    m.show_in_browser()
