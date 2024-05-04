from peewee import *
from src.mybootstrap_core_itskovichanton.orm import entity

from src.cherkizon.backend.entity.common import Deploy, Machine, HealthcheckResult

database = PostgresqlDatabase('cherkizon', **{'host': 'localhost', 'port': 3, 'user': 'postgres', 'password': '92559255'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database


@entity(HealthcheckResult)
class HealthcheckM(BaseModel):
    result = CharField(null=True)
    service_name = CharField(primary_key=True)
    time = DateTimeField()

    class Meta:
        table_name = 'healthcheck'


@entity(Machine)
class MachineM(BaseModel):
    description = CharField(null=True)
    env = CharField(null=True)
    ip = CharField(primary_key=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'machine'

