import datetime
from dataclasses import dataclass

from src.mybootstrap_core_itskovichanton.utils import hashed


@hashed
@dataclass
class User:
    username: str
    id: int
    name: str
    email: str = None
    telegram_username: str = None
    user_role: str = None


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

    def used_perc(self):
        return self.used / self.total


@hashed
@dataclass
class MachineInfo:
    ip: str = None
    available: bool = False  # машина доступна
    connection_error: str = None
    ram: MemoryVolume = None  # из free -h
    disk: MemoryVolume = None  # из df -h
    cpu: CPU = None
    etcd_port: int = None


@hashed
@dataclass
class HealthcheckResult:
    result: dict = None
    service_name: str = None
    time: datetime.datetime = None

    def is_failed(self) -> bool:
        return "error" in self.result


@hashed
@dataclass
class MachineHealthcheckResult:
    machine: MachineInfo = None
    symtomps: set = None
    time: datetime.datetime = None


@hashed
@dataclass
class Machine:
    ip: str = None
    name: str = None
    env: str = None
    description: str = None
    info: MachineInfo = None
    etcd_port: int = None


@hashed
@dataclass
class Deploy:
    port: str = None
    metrics_url: str = None
    last_start: datetime.datetime = None
    connection_error: str = None
    port_status: str = None
    pid: str = None
    status: str = None
    active: str = None
    load: str = None
    name: str = None
    systemd_name: str = None
    url: str = None
    internal_url: str = None
    machine: Machine = None
    version: str = None
    author: str = None
    env: str = None
    healthcheck_result: HealthcheckResult = None
    info: dict = None

    def get_url(self, protocol=None):
        if not protocol:
            protocol = "http"
        if protocol == "eureka":
            params = {"version": self.version, "env": self.env}
            params = [f"{key}={value}" for key, value in sorted(params.items()) if value]
            params = ",".join(params)
            return f"{protocol}://{self.name}[{params}]"
        return f"{protocol}://{self.machine.ip}:{self.port}"

    def prepare(self):
        self._prepare_creds()
        self.url = self.get_url(protocol="eureka")
        self.internal_url = self.get_url()

    def _prepare_creds(self):
        # 'cherkizon__name_reports__env_dev__author_aitskovich__version_master.service'
        self.systemd_name = self.name
        if self.name:
            n = self.name[11:len(self.name) - 8]
            n = n.split("__")
            for kv in n:
                try:
                    k, v = kv.split("_")
                    setattr(self, k, v)
                except:
                    ...
