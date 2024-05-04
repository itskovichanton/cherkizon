from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.exceptions import CoreException, \
    ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Deploy


class DeployControllerUseCase(Protocol):

    def execute(self, deploy_name: str, action: str, machine: str):
        ...


@bean
class DeployControllerUseCaseImpl(DeployControllerUseCase):
    agent: Agent

    def execute(self, deploy_name: str, action: str, machine: str):
        if action == "restart":
            return self.agent.restart_service(ip=machine, service=deploy_name)
        elif action == "stop":
            return self.agent.stop_service(ip=machine, service=deploy_name)
