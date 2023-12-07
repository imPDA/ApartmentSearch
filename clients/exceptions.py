from dataclasses import dataclass


@dataclass
class HTTPError(Exception):
    status_code: int
    response: str

    @property
    def message(self):
        return f"Unspecified error. Server responded with {self.status_code} status code, response: {self.response}"
