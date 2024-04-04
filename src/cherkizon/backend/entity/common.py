import datetime
from dataclasses import dataclass

from src.mybootstrap_core_itskovichanton.utils import hashed


@hashed
@dataclass
class CPU:
    load: float


@hashed
@dataclass
class MemoryVolume:
    available: int
    used: int
    total: int


@hashed
@dataclass
class MachineInfo:
    ip: str = None
    available: bool = False  # машина доступна
    connection_error: str = None
    ram: MemoryVolume = None  # из free -h
    disk: MemoryVolume = None  # из df -h
    cpu: CPU = None


@hashed
@dataclass
class Machine:
    ip: str = None
    name: str = None
    description: str = None
    info: MachineInfo = None


@hashed
@dataclass
class DeployStatus:
    port: str = None
    last_start: datetime.datetime = None
    connection_error: str = None
    port_status: str = None


@hashed
@dataclass
class Deploy:
    url: str = None
    internal_url: str = None
    machine: Machine = None
    version: str = None
    author: str = None
    service: str = None
    env: str = None
    status: DeployStatus = None

    def get_name(self) -> str:
        srv = self.service
        if isinstance(srv, Service):
            srv = srv.name
        return f"{srv}_v-{self.version}_env-{self.env}"

    def get_url(self, protocol=None):
        if not protocol:
            protocol = "http"
        if protocol == "eureka":
            service = self.service
            if isinstance(service, Service):
                service = service.name
            params = {"version": self.version, "env": self.env}
            params = [f"{key}={value}" for key, value in sorted(params.items()) if value]
            params = ",".join(params)
            return f"{protocol}://{service}[{params}]"
        return f"{protocol}://{self.machine.ip}:{self.status.port}"


@hashed
@dataclass
class Service:
    id: int = None
    name: str = None
