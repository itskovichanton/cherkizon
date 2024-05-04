from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.exceptions import CoreException, \
    ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND, ERR_REASON_VALIDATION

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.common.events import event_bus, EVENT_DEPLOY_RESTARTED, EVENT_DEPLOY_STOPPED


class DeployControllerUseCase(Protocol):

    def execute(self, deploy_name: str, action: str, machine: str):
        ...


@bean
class DeployControllerUseCaseImpl(DeployControllerUseCase):
    agent: Agent

    def execute(self, deploy_name: str, action: str, machine: str):
        if action == "restart":
            self.agent.restart_service(ip=machine, service=deploy_name)
        elif action == "stop":
            self.agent.stop_service(ip=machine, service=deploy_name)

        event_bus.emit(EVENT_DEPLOY_RESTARTED if action == "restart" else EVENT_DEPLOY_STOPPED,
                       deploy_name=deploy_name, action=action, machine=machine, threads=True)

        raise CoreException(message=f"Действие {action} не поддерживается", reason=ERR_REASON_VALIDATION)
