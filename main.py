import asyncio
import urllib.parse
import folium
from folium import DivIcon

from clients.domclick import DomclickClient
from datatypes import SearchParameters, DomclickOffer
from enums import DealType, Category, OfferType


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
        offer_type=['flat', 'layout'],
        # price=(None, 5_000_000),
        area=(50, None),
        # has_separated_bathrooms=True,
        renovation=('well_done', 'design'),
        has_lifts=True
    )

    return await client.get_all_offers(my_search)


if __name__ == '__main__':
    m = folium.Map(location=(58.6072106, 49.6223879), zoom_start=12)

    offers = asyncio.run(get_some_offers())
    offers.sort(key=lambda x: -x.price_info.square_price)

    sums = [offer.price_info.price for offer in offers]
    max_sum = max(sums)
    min_sum = min(sums)

    square_sums = [offer.price_info.square_price for offer in offers]
    max_square_sum = max(square_sums)
    min_square_sum = min(square_sums)

    def calculate_radius(sum: float, sum_range: tuple[float, float], map_to: tuple[float, float]) -> float:
        k = (map_to[1] - map_to[0]) / (sum_range[1] - sum_range[0])
        b = map_to[0] - k * sum_range[0]

        return k * sum + b

    def get_popup_info(offer: DomclickOffer) -> str:
        info = list([offer.address.display_name, ])
        info.append(f"{offer.price_info.price:,.0f} rub")
        info.append(f"{offer.price_info.square_price:,.0f} rub/sq.m.<br>{offer.object_info.area:.1f} sq.m.<br>{offer.object_info.rooms} room(s)")

        return '<br><br>'.join(info)

    for offer in offers:
        location = (offer.address.position.lat, offer.address.position.lon)

        iframe = folium.IFrame()
        popup = folium.Popup(get_popup_info(offer), max_width=200)

        folium.Circle(
            radius=calculate_radius(offer.price_info.square_price, (min_square_sum, max_square_sum), (10.0, 150.0)),
            location=location,
            popup=popup,
            color="#C30010",
            stroke=True,
            fill=True
        ).add_to(m)

        folium.map.Marker(
            location=location,
            icon=DivIcon(html=f'<div style="font-size: 8pt">{offer.object_info.area:.0f}</div>')
        ).add_to(m)

    m.show_in_browser()
