import json
from typing import Optional
from urllib.parse import urlencode

from pydantic import ValidationError

from datatypes import SearchParameters, DomclickOffer

from .http import HTTP


def store_outside(results: list, path: str):
    with open(path, 'w+', encoding='utf-8') as f:
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

        total_offers_count = response['result']['snippets_count']
        print(f'{total_offers_count} offers found...')  # TODO logging

        return total_offers_count

    def _try_to_convert_to_pydantic(self, raw_offers: list[dict]) -> (list[DomclickOffer], list[dict]):
        successful_converts = []
        unsuccessful_converts = []

        for raw_offer in raw_offers:
            try:
                successful_converts.append(DomclickOffer(**raw_offer))
            except ValidationError as e:
                raw_offer.update({'__errors': e.errors()})
                unsuccessful_converts.append(raw_offer)

        print(f"Success: {len(successful_converts)} / {len(raw_offers)} "
              f"({len(successful_converts) / len(raw_offers) * 100:.0f} %)")  # TODO logging

        return successful_converts, unsuccessful_converts

    async def get_all_offers(self, search_parameters: SearchParameters, *, parallel: bool = False) -> list[DomclickOffer]:
        if parallel:
            raw_offers = await self._retrieve_parallel(search_parameters)
        else:
            raw_offers = await self._retrieve_sequentially(search_parameters)

        successes, fails = self._try_to_convert_to_pydantic(raw_offers)

        store_outside(fails, 'fails.json')

        return successes

    async def _spawn_urls(self, search_parameters: SearchParameters, *, search_limit: int = 20) -> list[str]:
        OFFERS_ENDPOINT = 'https://research-api.domclick.ru/v5/offers'

        total_offers_count = await self.get_amount_of_offers(search_parameters)
        iterations = total_offers_count // search_limit + (1 if total_offers_count % search_limit else 0)

        urls = [
            self.build_url(
                OFFERS_ENDPOINT,
                search_parameters,
                limit=search_limit,
                offset=i * search_limit
            ) for i in range(iterations)
        ]

        print(urls)  # TODO logging debug

        return urls

    async def _retrieve_parallel(self, search_parameters: SearchParameters) -> list[dict]:
        raise NotImplementedError()

    async def _retrieve_sequentially(self, search_parameters: SearchParameters, *, search_limit: int = 20) -> list[dict]:
        urls = await self._spawn_urls(search_parameters, search_limit=search_limit)

        offers = []
        for i, url in enumerate(urls):
            response = await self.req('get', url)
            offers.extend(response['result']['items'])
            print(f'{i + 1} / {len(urls)} iterations')  # TODO logging

        return offers

    def build_url(self, endpoint: str, search_parameters: SearchParameters, *, limit: int = 20, offset: int = 0):
        query = search_parameters.q

        print(query)  # TODO logging debug

        some_more_stuff = {
            'offset': offset,
            'limit': limit,  # was 20
            'sort': 'qi',
            'sort_dir': 'desc',
            'sort_by_tariff_date': '1'
        }

        return f'{endpoint}?{urlencode(query, doseq=True)}&{urlencode(some_more_stuff)}'.replace('True', '1')
