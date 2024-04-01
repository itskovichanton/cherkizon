from dataclasses import dataclass
from typing import Protocol

from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Deploy, Machine
from src.cherkizon.backend.repo.deploy import DeployRepo
from src.cherkizon.backend.usecase.list_machines import ListMachinesUseCase


@dataclass
class DeployListing:
    deploys: list[Deploy]
    machines: list[Machine] = None


@dataclass
class WithMachinesOptions:
    enrich: bool = True
    with_info: bool = True


class ListDeploysUseCase(Protocol):

    def find(self, filter: Deploy = None, with_machines_options: WithMachinesOptions = None) -> DeployListing:
        ...


@bean
class ListDeploysUseCaseImpl(ListDeploysUseCase):
    deploy_repo: DeployRepo
    list_machines_uc: ListMachinesUseCase

    def find(self, filter: Deploy = None, with_machines_options: WithMachinesOptions = None) -> DeployListing:
        deploys = self.deploy_repo.find(filter)
        machines = {}
        for deploy in deploys:
            machines[deploy.machine.ip] = deploy.machine

        r = DeployListing(deploys=deploys)

        if not with_machines_options:
            with_machines_options = WithMachinesOptions()

        if with_machines_options.enrich:
            if with_machines_options.with_info:
                machine_infos = self.list_machines_uc.find(ips=list(machines.keys()))
                for ip, machine_info in machine_infos.items():
                    machines[ip].info = machine_info
                r.machines = list(machines.values())

        for deploy in deploys:
            deploy.service.id = None
            deploy.machine = None

        return r
