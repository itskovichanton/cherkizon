from dataclasses import dataclass
from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel, execute_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Machine, Deploy

from src.cherkizon.backend.repo.machine import MachineRepo
from src.cherkizon.backend.usecase.list_machines import ListMachinesUseCase


@dataclass
class DeployListing:
    deploys: list[Deploy] = None
    machines: list[Machine] = None


class ListDeploysUseCase(Protocol):

    def find(self, filter: Deploy = None, with_machines: bool = True) -> DeployListing:
        ...


@bean
class ListDeploysUseCaseImpl(ListDeploysUseCase):
    machine_repo: MachineRepo
    list_machines_uc: ListMachinesUseCase
    agent: Agent

    def init(self, **kwargs):
        return
        a = self.find(filter=Deploy(name="reports", env="dev"))
        print(a)

    def find(self, filter: Deploy = None, with_machines: bool = True) -> DeployListing:

        r = DeployListing(deploys=[], machines=set())

        def _get_deploys(machine: Machine):
            try:
                r = self.agent.get_deploys(ip=machine.ip, service=filter.name)
                for deploy in r:
                    deploy.machine = machine
                return r
            except BaseException as ex:
                return [Deploy(machine=machine, connection_error=str(ex))]

        machines = self.machine_repo.list(env=filter.env)
        for machine, deploys in calc_parallel(machines, _get_deploys).items():
            r.deploys.extend(deploys)
            if deploys and not deploys[0].connection_error:
                r.machines.add(machine.ip)

        if with_machines:
            r.machines = self.list_machines_uc.find(ips=r.machines)

        for deploy in r.deploys:
            deploy.prepare()

        return r
