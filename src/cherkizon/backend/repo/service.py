from typing import Protocol

from src.mybootstrap_core_itskovichanton.logger import log
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Service
from src.cherkizon.backend.repo.common import RepoActionResult, RepoAction
from src.cherkizon.backend.repo.db import DB


class ServiceRepo(Protocol):

    def save(self, s: Service) -> RepoActionResult:
        ...


@bean
class ServiceRepoImpl(ServiceRepo):
    db: DB

    # @to_real_entity
    # def list(self, filter: Service = None) -> list[Service]:
    #     return (ServiceModel
    #             .select(ServiceModel, GitlabModel)
    #             .join(GitlabModel, JOIN.INNER)
    #             .where(*infer_where(filter)))

    @log("repo", _action="save service")
    def save(self, s: Service) -> RepoActionResult:
        query = "SELECT id, was_updated FROM save_service(%s,%s,%s,%s,%s,%s,%s)"
        params = (s.name, s.description, s.gitlab_project_id, s.slack_channel_id, s.docs_url, s.repo, s.namespace.id)
        r = next(self.db.get().execute_sql(query, params))
        s.id = r[0]
        return RepoActionResult(entity=s,
                                action=RepoAction.UPDATED if r[1] else RepoAction.INSERTED)
