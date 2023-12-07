import asyncio
import urllib.parse
from pprint import pprint

from clients.domclick import DomclickClient
from datatypes import SearchParameters
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


if __name__ == '__main__':
    client = DomclickClient()

    my_search = SearchParameters(
        address='abf4ae61-af59-4b2d-a8d9-fdf9b47c4a5d',
        deal_type='sale',
        category='living',
        offer_type=['flat', 'layout'],
        price=(None, 4000000),
        has_separated_bathrooms=True,
        renovation=('well_done', 'design'),
        has_lifts=True
    )

    pprint(asyncio.run(client.get_all_offers(my_search)))
