from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import requests
from dacite import from_dict, Config
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_fastapi_itskovichanton.utils import parse_response

from src.cherkizon.backend.entity.common import MachineInfo, DeployStatus, Service


@dataclass
class _Config:
    port = 4001


class Agent(Protocol):

    def get_machine_info(self, ip: str) -> MachineInfo:
        ...

    def get_deploy_status(self, ip: str, service: Service | str) -> DeployStatus:
        ...


@bean(config=("agent", _Config, _Config()))
class AgentImpl(Agent):

    def init(self, **kwargs):
        self._session = requests.Session()
        self._session.timeout = 5

    def get_machine_info(self, ip: str) -> MachineInfo:
        r = self._call(ip, cl=MachineInfo, endpoint="get_machine_info")
        r.available = True
        r.ip = ip
        return r

    def get_deploy_status(self, ip: str, service: Service | str) -> DeployStatus:
        if isinstance(service, Service):
            service = service.name
        r = self._call(ip, endpoint="get_service_info", service=service)
        r = r[service]
        try:
            r["last_start"] = datetime.strptime(r["last_start"][3:], "%Y-%m-%dT%H:%M:%S%z")
        except:
            ...
        return DeployStatus(port=r["port_from_pid"], pid=r["pid"], port_status=r["port_status"],
                            last_start=r["last_start"])

    def _call(self, ip, endpoint, cl=None, **kwargs):
        r = self._session.get(url=f"http://{ip}:{self.config.port}/{endpoint}", params=kwargs)
        r = parse_response(r)
        if cl:
            r = from_dict(data_class=cl, data=r, config=Config(check_types=False))
        return r
