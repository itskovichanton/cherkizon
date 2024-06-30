from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import requests
from dacite import from_dict, Config
from src.mybootstrap_core_itskovichanton.utils import is_listable
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_fastapi_itskovichanton.utils import parse_response

from src.cherkizon.backend.entity.common import MachineInfo, Deploy


@dataclass
class _Config:
    port = 4001


class Agent(Protocol):

    def get_machine_info(self, ip: str) -> MachineInfo:
        ...

    def get_deploy_status(self, ip: str, service: str | str) -> Deploy:
        ...

    def get_deploys(self, ip: str, service: str | str) -> list[Deploy]:
        ...

    def restart_service(self, ip: str, service: str | str):
        ...

    def stop_service(self, ip: str, service: str | str):
        ...


@bean(config=("agent", _Config, _Config()))
class AgentImpl(Agent):

    def init(self, **kwargs):
        self._session = requests.Session()
        self._session.timeout = 5

    def get_deploys(self, ip: str, service: str | str) -> list[Deploy]:
        return self._call(ip, cl=list[Deploy], endpoint="find_services", service=service)

    def get_machine_info(self, ip: str) -> MachineInfo:
        r = self._call(ip, cl=MachineInfo, endpoint="get_machine_info")
        r.available = True
        r.ip = ip
        return r

    def stop_service(self, ip: str, service: str | str):
        return self._execute_action(ip, service, endpoint="stop_service")

    def restart_service(self, ip: str, service: str | str):
        return self._execute_action(ip, service, endpoint="restart_service")

    def _execute_action(self, ip: str, service: str | str, endpoint):
        return self._call(ip, endpoint, service=service)

    def get_deploy_status(self, ip: str, service: str | str) -> Deploy:
        r = self._call(ip, endpoint="get_service_info", service=service)
        r = r[service]
        try:
            r["last_start"] = datetime.strptime(r["last_start"][3:], "%Y-%m-%dT%H:%M:%S%z")
        except:
            ...
        return Deploy(port=r["port_from_pid"], port_status=r["port_status"], last_start=r["last_start"])

    def _call(self, ip, endpoint, cl=None, **kwargs):
        return parse_response(self._session.get(url=f"http://{ip}:{self.config.port}/{endpoint}", params=kwargs), cl=cl)
