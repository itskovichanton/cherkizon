from dataclasses import dataclass
from typing import Protocol

import requests
from dacite import from_dict, Config
from src.mybootstrap_core_itskovichanton.utils import is_listable
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_fastapi_itskovichanton.utils import parse_response
from src.mybootstrap_pyauth_itskovichanton.entities import AuthArgs

from src.cherkizon.backend.entity.common import User


@dataclass
class _Config:
    url: str = None
    s2s: AuthArgs = None


class PaaS(Protocol):

    def get_service_team(self, service: str) -> list[User]:
        ...


@bean(config=("paas", _Config, _Config()))
class PaaSImpl(PaaS):

    def init(self, **kwargs):
        self._session = requests.Session()
        if self.config.s2s:
            self._session.auth = (self.config.s2s.username, self.config.s2s.password)
        self._session.timeout = 5

    def get_service_team(self, service: str) -> list[User]:
        return parse_response(self._session.get(url=f"{self.config.url}/service/team", params={"service": service}),
                              cl=list[User])
