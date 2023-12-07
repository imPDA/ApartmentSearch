from abc import ABC, abstractmethod
from typing import Literal

from httpx import AsyncClient

from .exceptions import HTTPError

Method = Literal['get', 'post']


class HTTP(ABC):
    def __init__(self):
        pass

    async def req(self, method: Method, url: str, **kwargs) -> dict:
        async with AsyncClient() as client:
            response = await client.request(method, url, **kwargs)

        if response.status_code != 200:
            raise HTTPError(response.status_code, response.text)

        return response.json()

    @abstractmethod
    def get_all_offers(self, *args, **kwargs):
        raise NotImplementedError()
