from typing import Protocol

import gitlab
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Namespace, Service
from src.cherkizon.backend.repo.namespace import NamespaceRepo
from src.cherkizon.backend.repo.service import ServiceRepo


class SyncServicesUseCase(Protocol):

    def sync(self):
        ...


@bean
class SyncServicesUseCaseImpl(SyncServicesUseCase):
    namespaces_repo: NamespaceRepo
    services_repo: ServiceRepo

    def sync(self):
        for namespace in self.namespaces_repo.list():
            self._sync_for_namespace(namespace)

    def _sync_for_namespace(self, namespace: Namespace):
        gl = gitlab.Gitlab(namespace.gitlab.url, private_token=namespace.gitlab.token,
                           api_version=namespace.gitlab.api_version or "4")
        gl.auth()

        for project in gl.projects.list():
            if not project.archived:
                try:
                    self.services_repo.save(
                        Service(description=project.description,
                                gitlab_project_id=project.id,
                                name=project.name,
                                repo=project.web_url,
                                namespace=namespace,
                                docs_url=f"{namespace.gitlab.url}{project.wikis.path}"),
                    )
                except:
                    ...
