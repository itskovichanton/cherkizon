from typing import Protocol

from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Deploy, Machine
from src.cherkizon.backend.repo.deploy import DeployRepo


class RegisterDeployUseCase(Protocol):

    def register(self, deploy: Deploy):
        ...


@bean
class RegisterDeployUseCaseImpl(RegisterDeployUseCase):
    deploy_repo: DeployRepo

    def init(self, **kwargs):
        deploys = self.deploy_repo.find(filter=Deploy(author="aitskovich", machine=Machine(ip="192.168.200.156")))
        # self.register(
        #     Deploy(http_port=8082, version="feature/RFC-1232", env="dev", author="aitskovich", service="reports-kg",
        #            machine=Machine(ip="192.168.200.156", name="test-kg")))

    def register(self, deploy: Deploy):
        self.deploy_repo.save(deploy)
