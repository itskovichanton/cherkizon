from datetime import datetime, timedelta
import json
from dataclasses import dataclass

import requests
from paprika import threaded
from src.mybootstrap_core_itskovichanton.alerts import AlertService, Alert
from src.mybootstrap_core_itskovichanton.utils import repeat, hashed
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_fastapi_itskovichanton.utils import parse_response

from src.cherkizon.backend.entity.common import Deploy, HealthcheckResult, MachineHealthcheckResult
from src.cherkizon.backend.realtime_config import AlertIfDiskUsagePercentBiggerThanRealTimeConfigEntry, \
    AlertIfRAMUsagePercentBiggerThanRealTimeConfigEntry
from src.cherkizon.backend.repo.healthcheck import HealthcheckRepo
from src.cherkizon.backend.repo.machine_healthcheck import MachineHealthcheckRepo
from src.cherkizon.backend.usecase.list_deploys import ListDeploysUseCase
from src.cherkizon.backend.usecase.list_machines import ListMachinesUseCase
from src.cherkizon.common.events import event_bus, EVENT_DEPLOY_HEALTHCHECK_FAILED, EVENT_DEPLOY_HEALTHCHECK_FIXED, \
    EVENT_MACHINE_HEALTHCHECK_BAD, EVENT_MACHINE_HEALTHCHECK_FIXED, EVENT_MACHINE_DISK_OVER_USED, \
    EVENT_MACHINE_RAM_OVER_USED


@dataclass
class _Config:
    token: str = "f567a8da21a261ed67f46ba07defecd9"
    url: str = "http://localhost:9090/graph"


@bean(config=("healthcheck", _Config, _Config()))
class HealthcheckUseCase:
    list_deploys_uc: ListDeploysUseCase
    list_machines_uc: ListMachinesUseCase
    healthcheck_repo: HealthcheckRepo
    machine_healthcheck_repo: MachineHealthcheckRepo
    alerts: AlertService
    alert_if_disk_usage_percent_greater_than: AlertIfDiskUsagePercentBiggerThanRealTimeConfigEntry
    alert_if_ram_usage_percent_greater_than: AlertIfRAMUsagePercentBiggerThanRealTimeConfigEntry

    def init(self, **kwargs):
        self._session = requests.Session()
        self._session.timeout = 5
        self._check_statuses: dict[str, datetime] = {}
        self._start()

    @threaded
    @repeat(interval=60 * 10)
    def _start(self):
        deploys = self.list_deploys_uc.find().deploys
        for deploy in deploys:
            healthcheck_result = self._check_health(deploy)
            self.healthcheck_repo.save(healthcheck_result)
            self._process_healthcheck(deploy, healthcheck_result)

        for machine_ip, machine in self.list_machines_uc.find().items():

            self.machine_healthcheck_repo.save(machine)

            bad_health_symptoms = set()
            if machine.disk.used_perc() * 100 >= (self.alert_if_disk_usage_percent_greater_than.value or 80):
                bad_health_symptoms.add(EVENT_MACHINE_DISK_OVER_USED)
            if machine.ram.used_perc() * 100 >= (self.alert_if_ram_usage_percent_greater_than.value or 90):
                bad_health_symptoms.add(EVENT_MACHINE_RAM_OVER_USED)

            last_check_failed_time = self._check_statuses.get(machine_ip)
            if bad_health_symptoms:
                if (not last_check_failed_time) or (datetime.now() - last_check_failed_time > timedelta(minutes=10)):
                    self._check_statuses[machine_ip] = datetime.now()
                    event_bus.emit(EVENT_MACHINE_HEALTHCHECK_BAD, bad_health_symptoms, machine)
            elif last_check_failed_time:
                self._check_statuses.pop(machine_ip)
                event_bus.emit(EVENT_MACHINE_HEALTHCHECK_FIXED, machine)

    def _process_healthcheck(self, deploy: Deploy, healthcheck_result: HealthcheckResult):
        results = healthcheck_result.result.get("results")

        def is_failed(x: dict):
            passed = x.get("passed")
            return (not passed) and (type(passed) == bool)

        failed_checks = [x for x in results if is_failed(x)]
        last_check_failed_time = self._check_statuses.get(deploy.systemd_name)
        if failed_checks:
            if (not last_check_failed_time) or (datetime.now() - last_check_failed_time > timedelta(minutes=10)):
                self._check_statuses[deploy.systemd_name] = datetime.now()
                event_bus.emit(EVENT_DEPLOY_HEALTHCHECK_FAILED, deploy, healthcheck_result)
        elif last_check_failed_time:
            self._check_statuses.pop(deploy.systemd_name)
            event_bus.emit(EVENT_DEPLOY_HEALTHCHECK_FIXED, deploy, healthcheck_result)

    def _check_health(self, deploy: Deploy) -> HealthcheckResult:
        r = HealthcheckResult(service_name=deploy.systemd_name)
        try:
            req = self._session.get(url=f"{deploy.internal_url}/healthcheck",
                                    headers={"sessionToken": self.config.token})
            r.result = parse_response(req)
            if type(r.result) == str:
                r.result = json.loads(r.result)
        except BaseException as ex:
            r.result = {"error": {"message": str(ex)}}
        r.time = datetime.now()
        return r
