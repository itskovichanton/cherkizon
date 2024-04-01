from dataclasses import dataclass
from typing import Protocol

from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Machine, MachineInfo


@dataclass
class MachineListing:
    Machines: list[Machine]
    machines: list[Machine] = None


@dataclass
class WithMachinesOptions:
    enrich: bool = True
    with_health: bool = True


class ListMachinesUseCase(Protocol):

    def find(self, ips: list[str]) -> dict[str, MachineInfo]:
        ...


@bean
class ListMachinesUseCaseImpl(ListMachinesUseCase):

    def find(self, ips: list[str]) -> dict[str, MachineInfo]:
        return {"192.168.200.156": MachineInfo(ip="192.168.200.156"),
                "192.168.200.56": MachineInfo(ip="192.168.200.56", available=True)}
