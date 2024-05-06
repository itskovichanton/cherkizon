import datetime
import json

from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.cherkizon.backend.entity.common import Deploy, HealthcheckResult
from src.cherkizon.backend.usecase.deploy_actions import DeployControllerUseCase, DEPLOY_ACTION_RESTART
from src.cherkizon.common.events import event_bus, EVENT_HEALTHCHECK_RESULT_RECEIVED


@bean
class DeployReanimatorUseCase:
    list_controller_uc: DeployControllerUseCase

    def _react_on_healthcheck(self, deploy: Deploy, healthcheck_result: HealthcheckResult):
        if healthcheck_result.is_failed():
            self.list_controller_uc.execute(deploy_name=deploy.systemd_name, action=DEPLOY_ACTION_RESTART,
                                            machine=deploy.machine.ip)

    def init(self, **kwargs):
        event_bus.add_event(EVENT_HEALTHCHECK_RESULT_RECEIVED, self._react_on_healthcheck)
