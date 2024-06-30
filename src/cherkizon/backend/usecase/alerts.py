import json
from datetime import datetime, date

from src.mybootstrap_core_itskovichanton.alerts import AlertService, Alert
from src.mybootstrap_core_itskovichanton.utils import to_dict_deep, encode_json_value
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.apis.paas import PaaS
from src.cherkizon.backend.entity.common import Deploy, HealthcheckResult, MachineInfo
from src.cherkizon.common.events import event_bus, EVENT_DEPLOY_HEALTHCHECK_FAILED, EVENT_DEPLOY_RESTARTED, \
    EVENT_DEPLOY_STOPPED, EVENT_DEPLOY_HEALTHCHECK_FIXED, EVENT_MACHINE_HEALTHCHECK_BAD, EVENT_MACHINE_HEALTHCHECK_FIXED


@bean
class Alerts:
    alerts: AlertService
    paas_api: PaaS

    def send_to_machine_team(self, obj, ip, message, level=0):
        teammates = self.paas_api.get_machine_team(ip)
        if teammates:
            message += f"\n\nObject: \n{json.dumps(obj)}"
            self.alerts.send(Alert(subject=obj,
                                   level=level,
                                   message=message,
                                   emails=[tm.email for tm in teammates]),
                             )

    def send_to_deploy_team(self, obj, service_name, message, level=0):
        teammates = self.paas_api.get_service_team(service_name)
        if teammates:
            message += f"\n\nObject: \n{json.dumps(obj)}"
            self.alerts.send(Alert(subject=obj,
                                   level=level,
                                   message=message,
                                   emails=[tm.email for tm in teammates]),
                             )

    def _on_healthcheck_failed(self, deploy: Deploy, healthcheck_result: HealthcheckResult):
        self.send_to_deploy_team(obj=f"Healthcheck упал при проверке сервиса '{deploy.name}-{deploy.env}'",
                                 message=json.dumps(to_dict_deep(healthcheck_result, value_mapper=encode_json_value)),
                                 service_name=deploy.name,
                                 level=5)

    def _on_healthcheck_fixed(self, deploy: Deploy, healthcheck_result: HealthcheckResult):
        self.send_to_deploy_team(obj=f"Healthcheck восстановился для сервиса '{deploy.name}-{deploy.env}'",
                                 message=json.dumps(to_dict_deep(healthcheck_result, value_mapper=encode_json_value)),
                                 service_name=deploy.name,
                                 level=5)

    def _on_deploy_stopped(self, deploy_name: str, action: str, machine: str):
        ...

    def _on_deploy_restarted(self, deploy_name: str, action: str, machine: str):
        ...
        # self.send_to_deploy_team(obj=f"Действие '{action}' с деплоем '{deploy_name}'",
        #                          message="",
        #                          service_name=deploy.name,
        #                          level=5)

    def _on_machine_healthcheck_bad(self, symptoms: set, machine: MachineInfo):
        self.send_to_machine_team(obj=f"Healthcheck машины {machine.ip} показал плохое здоровье",
                                  message=f"Симптомы: {symptoms}. Детали: {json.dumps(to_dict_deep(machine, value_mapper=encode_json_value))}",
                                  ip=machine.ip,
                                  level=5)

    def _on_machine_healthcheck_fixed(self, machine: MachineInfo):
        self.send_to_machine_team(obj=f"Healthcheck машины {machine.ip} показал стабилизацию здоровья",
                                  message=f"Детали: {json.dumps(to_dict_deep(machine, value_mapper=encode_json_value))}",
                                  ip=machine.ip,
                                  level=5)

    def init(self, **kwargs):
        event_bus.add_event(self._on_machine_healthcheck_bad, EVENT_MACHINE_HEALTHCHECK_BAD)
        event_bus.add_event(self._on_machine_healthcheck_fixed, EVENT_MACHINE_HEALTHCHECK_FIXED)
        event_bus.add_event(self._on_healthcheck_failed, EVENT_DEPLOY_HEALTHCHECK_FAILED)
        event_bus.add_event(self._on_healthcheck_fixed, EVENT_DEPLOY_HEALTHCHECK_FIXED)
        event_bus.add_event(self._on_deploy_stopped, EVENT_DEPLOY_RESTARTED)
        event_bus.add_event(self._on_deploy_restarted, EVENT_DEPLOY_STOPPED)
