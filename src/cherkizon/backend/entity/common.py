from dataclasses import dataclass


@dataclass
class MemoryVolume:
    available: int
    all: int


@dataclass
class MachineInfo:
    ip: str
    available: bool = False  # машина доступна
    ram: MemoryVolume = None  # из free -h
    disk: MemoryVolume = None  # из df -h


@dataclass
class Machine:
    ip: str = None
    name: str = None
    description: str = None
    info: MachineInfo = None


@dataclass
class DeployHealth:
    available: bool  # порт доступен
    status: str  # из systemctl (todo: сделай enum)
    err_log: str = None  # хвост лога ошибок


@dataclass
class Deploy:
    machine: Machine = None
    version: str = None
    author: str = None
    service: str = None
    http_port: int = None
    env: str = None
    health: DeployHealth = None


@dataclass
class Service:
    id: int = None
    name: str = None
