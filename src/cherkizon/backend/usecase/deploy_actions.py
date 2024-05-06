from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.exceptions import CoreException, \
    ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND, ERR_REASON_VALIDATION

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.common.events import event_bus, EVENT_DEPLOY_RESTARTED, EVENT_DEPLOY_STOPPED

DEPLOY_ACTION_RESTART = "restart"
DEPLOY_ACTION_STOP = "stop"


class DeployControllerUseCase(Protocol):

    def execute(self, deploy_name: str, action: str, machine: str):
        ...


@bean
class DeployControllerUseCaseImpl(DeployControllerUseCase):
    agent: Agent

    def execute(self, deploy_name: str, action: str, machine: str):
        r = None
        if action == DEPLOY_ACTION_RESTART:
            r = self.agent.restart_service(ip=machine, service=deploy_name)
        elif action == DEPLOY_ACTION_STOP:
            r = self.agent.stop_service(ip=machine, service=deploy_name)

        event = EVENT_DEPLOY_RESTARTED if action == DEPLOY_ACTION_RESTART else EVENT_DEPLOY_STOPPED
        event_bus.emit(event, deploy_name=deploy_name, action=action, machine=machine, threads=True)
        if r:
            return r

        raise CoreException(message=f"Действие {action} не поддерживается", reason=ERR_REASON_VALIDATION)
