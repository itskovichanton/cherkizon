import json
from typing import Protocol

from src.mybootstrap_core_itskovichanton.orm import to_real_entity
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Deploy, Machine, HealthcheckResult
from src.cherkizon.backend.repo.db import DB
from src.cherkizon.backend.repo.schema import MachineM, HealthcheckM


class HealthcheckRepo(Protocol):

    def save(self, r: HealthcheckResult):
        ...

    def list(self, services: list[str] = None) -> list[HealthcheckResult]:
        ...


@bean
class HealthcheckRepoImpl(HealthcheckRepo):
    db: DB

    @to_real_entity
    def _list(self, services: list[str] = None) -> list[HealthcheckResult]:
        r = HealthcheckM.select(HealthcheckM)
        if services:
            r = r.where(HealthcheckM.service_name << services)
        return r

    def list(self, services: list[str] = None) -> list[HealthcheckResult]:
        r = self._list(services)
        if r:
            for hc in r:
                hc.result = json.loads(hc.result)
        return r

    def save(self, r: HealthcheckResult):
        m = HealthcheckM()
        m.result = json.dumps(r.result)
        m.time = r.time
        m.service_name = r.service_name
        m.save(force_insert=True)

    # @to_real_entity
    # def list(self, env: str = None) -> list[Machine]:
    #     m = MachineM.select(MachineM)
    #     if env:
    #         m = m.where(MachineM.env == env)
    #     return m
