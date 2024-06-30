from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.pipeline import ActionRunner

from src.cherkizon.backend.entity.common import Deploy

from src.cherkizon.backend.usecase.get_deploy_url import GetDeployUrlUseCase
from src.cherkizon.backend.usecase.list_deploys import ListDeploysUseCase, DeployListing

from src.cherkizon.backend.usecase.deploy_actions import DeployControllerUseCase


@bean
class Controller:
    action_runner: ActionRunner
    get_deploy_uc: GetDeployUrlUseCase
    restart_deploy_uc: DeployControllerUseCase
    list_deploys_uc: ListDeploysUseCase
    list_deploy_etcds_uc: ListDeploysUseCase

    async def execute_action_on_deploy(self, deploy_name: str, action: str, machine: str):
        def execute_action(arg):
            return self.restart_deploy_uc.execute(deploy_name, action, machine)

        return await self.action_runner.run(execute_action, call=None)

    async def list_deploys(self, filter: Deploy):
        def preprocess(r: DeployListing):
            for deploy in r.deploys:
                deploy.machine = deploy.machine.ip
            return r

        return await self.action_runner.run(self.list_deploys_uc.find, preprocess, call=filter)

    async def list_deploys_etcds(self, filter: Deploy):
        def preprocess(r: DeployListing):
            for deploy in r.deploys:
                deploy.machine = deploy.machine.ip
            return r

        return await self.action_runner.run(self.list_deploys_uc.find, preprocess, call=filter)

    async def get_internal_url(self, url: str):
        return await self.action_runner.run(self.get_deploy_uc.compile_url, call=url)
