from peewee import *
from src.mybootstrap_core_itskovichanton.di import injector
from src.mybootstrap_core_itskovichanton.orm import entity

from src.cherkizon.backend.entity.common import Namespace, Gitlab, Service
from src.cherkizon.backend.repo.db import DB

db = injector().inject(DB)


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = db.get()


class EnvironmentModel(BaseModel):
    name = CharField(unique=True)

    class Meta:
        table_name = 'environment'


@entity(Gitlab)
class GitlabModel(BaseModel):
    token = CharField(null=True)
    url = CharField()
    api_version = IntegerField(null=True)

    class Meta:
        table_name = 'gitlab'


@entity(Namespace)
class NamespaceModel(BaseModel):
    active = BooleanField(constraints=[SQL("DEFAULT true")])
    comment = TextField(null=True)
    gitlab = ForeignKeyField(column_name='gitlab_id', field='id', model=GitlabModel)
    name = CharField(unique=True)

    class Meta:
        table_name = 'namespace'


class PersonModel(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    deleted_at = DateTimeField(null=True)
    email = CharField(unique=True)
    gitlab_id = IntegerField(null=True)
    is_active = BooleanField(constraints=[SQL("DEFAULT true")])
    name = CharField(null=True)
    password = CharField(null=True)
    phone = CharField(null=True, unique=True)
    position = CharField()
    updated_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    username = CharField(unique=True)

    class Meta:
        table_name = 'person'


class RolesModel(BaseModel):
    name = CharField()

    class Meta:
        table_name = 'roles'


@entity(Service)
class ServiceModel(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    deleted_at = DateTimeField(null=True)
    description = TextField(null=True)
    docs_url = CharField(null=True)
    gitlab_project_id = IntegerField(null=True, unique=True)
    name = CharField(unique=True)
    namespace = ForeignKeyField(column_name='namespace_id', field='id', model=NamespaceModel)
    repo = CharField(unique=True)
    slack_channel_id = IntegerField(null=True)

    class Meta:
        table_name = 'service'


class ServicePersonRolesModel(BaseModel):
    person = ForeignKeyField(column_name='person_id', field='id', model=PersonModel, null=True)
    role = ForeignKeyField(column_name='role_id', field='id', model=RolesModel, null=True)
    service = ForeignKeyField(column_name='service_id', field='id', model=ServiceModel, null=True)

    class Meta:
        table_name = 'service_person_roles'
        primary_key = False
