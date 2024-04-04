from dataclasses import dataclass
from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel, execute_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Deploy, Machine, DeployStatus
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
    agent: Agent

    def init(self, **kwargs):
        return
        a = self.find(filter=Deploy(service=8))
        print(a)

    def find(self, filter: Deploy = None, with_machines_options: WithMachinesOptions = None) -> DeployListing:
        deploys = self.deploy_repo.find(filter)
        machines = {}
        for deploy in deploys:
            machines[deploy.machine.ip] = deploy.machine

        r = DeployListing(deploys=deploys)

        if not with_machines_options:
            with_machines_options = WithMachinesOptions()

        self._enrich_with_data(r, machines, with_machines_options, deploys)

        return r

    def _enrich_with_deploy_info(self, deploys: list[Deploy]):
        def _get_deploy_info(deploy: Deploy):
            try:
                return self.agent.get_deploy_status(ip=deploy.machine.ip, service=deploy.service)
            except BaseException as ex:
                return DeployStatus(connection_error=str(ex))

        deploy_dict = {deploy.get_name(): deploy for deploy in deploys}
        for deploy, deploy_info in calc_parallel(deploys, _get_deploy_info).items():
            deploy_dict[deploy.get_name()].status = deploy_info

    def _enrich_with_machines(self, r: DeployListing, machines):
        machine_infos = self.list_machines_uc.find(ips=set(machines.keys()))
        for ip, machine_info in machine_infos.items():
            machines[ip].info = machine_info
        r.machines = list(machines.values())

    def _enrich_with_data(self, r: DeployListing, machines, with_machines_options, deploys):
        execute_parallel(
            [
                (self._enrich_with_machines, [r, machines,
                                              with_machines_options])
                if (with_machines_options.enrich and with_machines_options.with_info) else None,
                (self._enrich_with_deploy_info, [deploys]),
            ],
        )
