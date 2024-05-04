import datetime
import json
from dataclasses import dataclass

import requests
from paprika import threaded
from src.mybootstrap_core_itskovichanton.alerts import AlertService, Alert
from src.mybootstrap_core_itskovichanton.utils import repeat
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_fastapi_itskovichanton.utils import parse_response

from src.cherkizon.backend.entity.common import Deploy, HealthcheckResult
from src.cherkizon.backend.repo.healthcheck import HealthcheckRepo
from src.cherkizon.backend.usecase.list_deploys import ListDeploysUseCase
from src.cherkizon.common.events import event_bus, EVENT_HEALTHCHECK_RESULT_RECEIVED


@dataclass
class _Config:
    token: str = "f567a8da21a261ed67f46ba07defecd9"
    url: str = "http://localhost:9090/graph"


@bean(config=("healthcheck", _Config, _Config()))
class HealthcheckUseCase:
    list_deploys_uc: ListDeploysUseCase
    healthcheck_check: HealthcheckRepo
    alerts: AlertService

    def init(self, **kwargs):
        self._session = requests.Session()
        self._session.timeout = 5
        self._start()

    @threaded
    @repeat(interval=60 * 10)
    def _start(self):
        deploys = self.list_deploys_uc.find(with_machines=False).deploys
        for deploy in deploys:
            healthcheck_result = self._check_health(deploy)
            self.healthcheck_check.save(healthcheck_result)
            self.alerts.send(
                Alert(
                    message=f"Healthcheck деплоя '{deploy.systemd_name}' завершился с ошибкой\n\n{healthcheck_result.result}")
            )
            event_bus.emit(EVENT_HEALTHCHECK_RESULT_RECEIVED, deploy=deploy, healthcheck_result=healthcheck_result,
                           threads=True)

    def _check_health(self, deploy: Deploy) -> HealthcheckResult:
        r = HealthcheckResult(service_name=deploy.systemd_name)
        try:
            req = self._session.get(url=f"{deploy.internal_url}/healthcheck",
                                    headers={"sessionToken": self.config.token})
            r.result = parse_response(req)
        except BaseException as ex:
            r.result = {"error": {"message": str(ex)}}
        r.time = datetime.datetime.now()
        return r
