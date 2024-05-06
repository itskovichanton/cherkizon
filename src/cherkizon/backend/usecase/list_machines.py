from dataclasses import dataclass
from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Machine, MachineInfo
from src.cherkizon.backend.repo.machine import MachineRepo


@dataclass
class MachineListing:
    Machines: list[Machine]
    machines: list[Machine] = None


@dataclass
class WithMachinesOptions:
    enrich: bool = True
    with_health: bool = True


class ListMachinesUseCase(Protocol):

    def find(self, ips: set[str] = None) -> dict[str, MachineInfo]:
        ...


@bean
class ListMachinesUseCaseImpl(ListMachinesUseCase):
    agent: Agent
    machine_repo: MachineRepo

    def find(self, ips: set[str] = None) -> dict[str, MachineInfo]:

        def _get_machine_info(ip):
            try:
                return self.agent.get_machine_info(ip)
            except BaseException as ex:
                return MachineInfo(available=False, ip=ip, connection_error=str(ex))

        if not ips:
            ips = [x.ip for x in self.machine_repo.list()]

        return calc_parallel(ips, _get_machine_info)
