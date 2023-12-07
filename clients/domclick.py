import json
from typing import Optional
from urllib.parse import urlencode

from datatypes import SearchParameters, DomclickOffer
from try_to_pydantic import try_with
from .http import HTTP


def store_outside(results: list):
    with open('results.json', 'w+', encoding='utf-8') as f:
        try:
            data: list = json.load(f)
        except json.decoder.JSONDecodeError:
            data = []

        data.extend(results)

        json.dump(data, f)


class DomclickClient(HTTP):
    def __init__(self):
        super().__init__()
        self.search_parameters: Optional[SearchParameters] = None

    async def get_amount_of_offers(self, search_parameters: SearchParameters) -> int:
        COUNT_ENDPOINT = 'https://research-api.domclick.ru/v7/offers/count'
        url = self.build_url(COUNT_ENDPOINT, search_parameters)

        response = await self.req('get', url)
        return response['result']['snippets_count']

    async def get_all_offers(self, search_parameters: SearchParameters) -> list[DomclickOffer]:
        OFFERS_ENDPOINT = 'https://research-api.domclick.ru/v5/offers'
        search_limit = 20
        total_offers = await self.get_amount_of_offers(search_parameters)

        iterations = total_offers // search_limit + (1 if total_offers % search_limit else 0)

        print(f'{total_offers} offers found...')  # TODO logging

        for i in range(iterations):
            url = self.build_url(OFFERS_ENDPOINT, search_parameters, limit=search_limit, offset=search_limit * i)

            response = await self.req('get', url)

            offers = response['result']['items']

            # store_outside(offers)

            try_with(offers)

            print(f'{i + 1} / {iterations}')
            # return response['result']['items']

    def build_url(self, endpoint: str, search_parameters: SearchParameters, *, limit: int = 30, offset: int = 0):
        query = search_parameters.q

        some_more_stuff = {
            'offset': offset,
            'limit': limit,  # was 20
            'sort': 'qi',
            'sort_dir': 'desc',
            'sort_by_tariff_date': '1'
        }

        return f'{endpoint}?{urlencode(query, doseq=True)}&{urlencode(some_more_stuff)}'
