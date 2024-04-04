from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.pipeline import ActionRunner

from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.backend.usecase.get_deploy_url import GetDeployUrlUseCase
from src.cherkizon.backend.usecase.list_deploys import ListDeploysUseCase, DeployListing
from src.cherkizon.backend.usecase.register_deploy import RegisterDeployUseCase
from src.cherkizon.backend.usecase.deploy_actions import DeployControllerUseCase


@bean
class Controller:
    action_runner: ActionRunner
    register_deploy_uc: RegisterDeployUseCase
    get_deploy_uc: GetDeployUrlUseCase
    restart_deploy_uc: DeployControllerUseCase
    list_deploys_uc: ListDeploysUseCase

    async def execute_action_on_deploy(self, deploy: Deploy, action):
        def preprocess(r: dict[Deploy, str]):
            return {d.get_name(): {"deploy": d, "result": result} for d, result in r.items()}

        if action == "restart":
            action = self.restart_deploy_uc.restart
        elif action == "stop":
            action = self.restart_deploy_uc.stop

        return await self.action_runner.run(action, preprocess, call=deploy)

    async def register_deploy(self, deploy: Deploy):
        return await self.action_runner.run(self.register_deploy_uc.register, call={"deploy": deploy})

    async def list_deploys(self, filter: Deploy):
        def preprocess(r: DeployListing):
            for deploy in r.deploys:
                deploy.machine = deploy.machine.ip
                deploy.service = deploy.service.name
            return r

        return await self.action_runner.run(self.list_deploys_uc.find, preprocess, call=filter)

    async def get_internal_url(self, url: str):
        return await self.action_runner.run(self.get_deploy_uc.compile_url, call=url)
