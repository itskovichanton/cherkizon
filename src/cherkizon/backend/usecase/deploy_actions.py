from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.exceptions import CoreException, \
    ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.backend.repo.deploy import DeployRepo


class DeployControllerUseCase(Protocol):

    def restart(self, deploy: Deploy):
        ...

    def stop(self, deploy: Deploy):
        ...


@bean
class DeployControllerUseCaseImpl(DeployControllerUseCase):
    deploy_repo: DeployRepo
    agent: Agent

    def init(self, **kwargs):
        ...
        # deploys = self.deploy_repo.find(filter=Deploy(author="aitskovich", machine=Machine(ip="192.168.200.156")))
        # self.register(
        #     Deploy(http_port=8082, version="feature/RFC-1232", env="dev", author="aitskovich", service="reports-kg",
        #            machine=Machine(ip="192.168.200.156", name="test-kg")))

    def restart(self, deploys: Deploy):
        return self._execute_deploy_action(deploys, "restart")

    def stop(self, deploys: Deploy):
        return self._execute_deploy_action(deploys, "stop")

    def _execute_deploy_action(self, deploys: Deploy, action):
        deploys = self.deploy_repo.find(deploys)
        if len(deploys) == 0:
            raise CoreException(message="Деплой не найден", reason=ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND)

        def execute_action(deploy):
            try:
                if action == "restart":
                    return self.agent.restart_service(ip=deploy.machine.ip, service=deploy.service)
                elif action == "stop":
                    return self.agent.stop_service(ip=deploy.machine.ip, service=deploy.service)
            except BaseException as ex:
                return {"failure": str(ex)}

        return calc_parallel(deploys, execute_action)
