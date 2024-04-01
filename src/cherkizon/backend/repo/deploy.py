from typing import Protocol

from src.mybootstrap_core_itskovichanton.orm import infer_where, to_real_entity
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.backend.repo.db import DB
from src.cherkizon.backend.repo.schema import DeployM, ServiceM, MachineM


class DeployRepo(Protocol):

    def save(self, deploy: Deploy):
        ...

    def find(self, filter: Deploy = None) -> list[Deploy]:
        ...


@bean
class DeployRepoImpl(DeployRepo):
    db: DB

    def save(self, s: Deploy):
        query = "SELECT * FROM save_deploy(%s,%s,%s,%s,%s,%s)"
        params = (s.version, s.service, s.author, s.machine.ip, s.http_port, s.env)
        self.db.get().execute_sql(query, params).close()

    @to_real_entity
    def find(self, filter: Deploy = Deploy()) -> list[Deploy]:
        return (DeployM.select(DeployM, MachineM, ServiceM)
                .join(MachineM, on=(DeployM.machine == MachineM.ip))
                .join(ServiceM, on=(DeployM.service == ServiceM.id))
                .where(*infer_where(filter)))
