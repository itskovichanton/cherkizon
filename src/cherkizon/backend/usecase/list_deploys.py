from dataclasses import dataclass
from typing import Protocol

from src.mybootstrap_core_itskovichanton.metrics_export import MetricsExporter
from src.mybootstrap_core_itskovichanton.utils import calc_parallel, execute_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Machine, Deploy
from src.cherkizon.backend.repo.healthcheck import HealthcheckRepo

from src.cherkizon.backend.repo.machine import MachineRepo
from src.cherkizon.backend.usecase.list_machines import ListMachinesUseCase


@dataclass
class DeployListing:
    deploys: list[Deploy] = None
    machines: list[Machine] = None


class ListDeploysUseCase(Protocol):

    def find(self, filter: Deploy = None, with_machines: bool = True, with_healthcheck: bool = True) -> DeployListing:
        ...


@bean
class ListDeploysUseCaseImpl(ListDeploysUseCase):
    machine_repo: MachineRepo
    list_machines_uc: ListMachinesUseCase
    healthcheck_repo: HealthcheckRepo
    agent: Agent
    me: MetricsExporter

    def init(self, **kwargs):
        return
        # a = self.find(filter=Deploy(name="reports", env="dev"))
        a = self.find(with_healthcheck=True)
        # print(a)

    def find(self, filter: Deploy = None, with_machines: bool = True, with_healthcheck: bool = True) -> DeployListing:

        if not filter:
            filter = Deploy()

        r = DeployListing(deploys=[], machines=set())

        def _get_deploys(m: Machine):
            try:
                deploys_on_machine = self.agent.get_deploys(ip=m.ip, service=filter.name)
                for dpl in deploys_on_machine:
                    dpl.machine = m
                return deploys_on_machine
            except BaseException as ex:
                return [Deploy(machine=m, connection_error=str(ex))]

        machines = self.machine_repo.list(env=filter.env)
        for machine, deploys in calc_parallel(machines, _get_deploys).items():
            r.deploys.extend(deploys)
            if deploys and not deploys[0].connection_error:
                r.machines.add(machine.ip)

        if with_machines:
            r.machines = self.list_machines_uc.find(ips=r.machines)

        for deploy in r.deploys:
            deploy.prepare()
            deploy.metrics_url = self.me.get_metrics_url(deploy.systemd_name)

        if with_healthcheck:
            healthchecks = self.healthcheck_repo.list(services=[d.systemd_name for d in r.deploys])
            if healthchecks:
                healthchecks = {hc.service_name: hc for hc in healthchecks}
                for deploy in r.deploys:
                    deploy.healthcheck_result = healthchecks.get(deploy.systemd_name)

        return r
