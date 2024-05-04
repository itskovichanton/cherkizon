from typing import Protocol

from src.mybootstrap_core_itskovichanton.orm import infer_where, to_real_entity
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Deploy, Machine
from src.cherkizon.backend.repo.db import DB
from src.cherkizon.backend.repo.schema import MachineM


class MachineRepo(Protocol):

    def get(self, ip: str) -> Machine:
        ...

    def list(self, env: str = None) -> list[Machine]:
        ...


@bean
class MachineRepoImpl(MachineRepo):
    db: DB

    @to_real_entity
    def get(self, ip: str) -> Machine:
        return MachineM.select(MachineM).where(MachineM.ip) or None

    @to_real_entity
    def list(self, env: str = None) -> list[Machine]:
        m = MachineM.select(MachineM)
        if env:
            m = m.where(MachineM.env == env)
        return m
