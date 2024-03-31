from typing import Protocol

from peewee import JOIN
from src.mybootstrap_core_itskovichanton.orm import to_real_entity, infer_where
from src.mybootstrap_ioc_itskovichanton.ioc import bean

from src.cherkizon.backend.entity.common import Namespace
from src.cherkizon.backend.repo.schema import NamespaceModel, GitlabModel


class NamespaceRepo(Protocol):

    def list(self, filter: Namespace = Namespace(active=True)) -> list[Namespace]:
        ...


@bean
class NamespaceRepoImpl(NamespaceRepo):

    @to_real_entity
    def list(self, filter: Namespace = Namespace(active=True)) -> list[Namespace]:
        return (NamespaceModel
                .select(NamespaceModel, GitlabModel)
                .join(GitlabModel, JOIN.INNER)
                .where(*infer_where(filter)))
