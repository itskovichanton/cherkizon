import datetime
import json
from typing import Protocol

from src.mybootstrap_core_itskovichanton.orm import to_real_entity
from src.mybootstrap_core_itskovichanton.utils import to_dict_deep
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Deploy, Machine, HealthcheckResult, MachineHealthcheckResult, \
    MachineInfo
from src.cherkizon.backend.repo.db import DB
from src.cherkizon.backend.repo.schema import MachineM, HealthcheckM, MachineHealthcheckM


class MachineHealthcheckRepo(Protocol):

    def save(self, r: MachineHealthcheckResult):
        ...

    def list(self, ips: list[str] = None) -> list[MachineHealthcheckResult]:
        ...


@bean
class MachineHealthcheckRepoImpl(MachineHealthcheckRepo):
    db: DB

    @to_real_entity
    def _list(self, ips: list[str] = None) -> list[MachineHealthcheckResult]:
        r = MachineHealthcheckM.select(MachineHealthcheckM)
        if ips:
            r = r.where(MachineHealthcheckM.ip << ips)
        return r

    def list(self, ips: list[str] = None) -> list[MachineHealthcheckResult]:
        r = self._list(ips)
        if r:
            for hc in r:
                hc.machine = json.loads(hc.machine)
        return r

    def save(self, r: MachineHealthcheckResult):
        m = MachineHealthcheckM()
        m.result = json.dumps(to_dict_deep(r))
        m.time = datetime.datetime.now()
        m.ip = r.machine.ip
        try:
            m.save(force_insert=True)
        except:
            m.save(force_insert=False)
