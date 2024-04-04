from peewee import *
from src.mybootstrap_core_itskovichanton.orm import entity

from src.cherkizon.backend.entity.common import Deploy, Service, Machine

database = PostgresqlDatabase('cherkizon',
                              **{'host': 'localhost', 'port': 3, 'user': 'postgres', 'password': '92559255'})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


@entity(Machine)
class MachineM(BaseModel):
    description = CharField(null=True)
    ip = CharField(primary_key=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'machine'


@entity(Service)
class ServiceM(BaseModel):
    id = BigAutoField()
    name = CharField(null=True, unique=True)

    class Meta:
        table_name = 'service'


@entity(Deploy)
class DeployM(BaseModel):
    author = CharField()
    env = CharField()
    machine = ForeignKeyField(column_name='machine_ip', field='ip', model=MachineM)
    service = ForeignKeyField(column_name='service_id', field='id', model=ServiceM)
    version = CharField()
    is_deleted: BooleanField()

    class Meta:
        table_name = 'deploy'
        indexes = (
            (('service', 'env', 'version'), True),
        )
        primary_key = CompositeKey('env', 'service', 'version')
