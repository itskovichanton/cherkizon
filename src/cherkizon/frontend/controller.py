from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.pipeline import ActionRunner

from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.backend.usecase.list_deploys import ListDeploysUseCase
from src.cherkizon.backend.usecase.register_deploy import RegisterDeployUseCase


@bean
class Controller:
    action_runner: ActionRunner
    register_deploy_uc: RegisterDeployUseCase
    list_deploys_uc: ListDeploysUseCase

    async def register_deploy(self, deploy: Deploy):
        return await self.action_runner.run(self.register_deploy_uc.register, call={"deploy": deploy})

    async def list_deploys(self, filter: Deploy):
        return await self.action_runner.run(self.list_deploys_uc.find, call=filter)
