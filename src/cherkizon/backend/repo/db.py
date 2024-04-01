from dataclasses import dataclass
from typing import Protocol

import psycopg2
from paprika import singleton
from peewee import PostgresqlDatabase
from src.mybootstrap_ioc_itskovichanton.ioc import bean


class DB(Protocol):

    def get(self) -> PostgresqlDatabase:
        ...

    def get_psycopg2_connection(self):
        ...


@dataclass
class _Config:
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432


@bean(cfg=("db", _Config))
class DBImpl(DB):

    @singleton
    def get(self) -> PostgresqlDatabase:
        return PostgresqlDatabase('cherkizon', **self.cfg.__dict__)

    @singleton
    def get_psycopg2_connection(self):
        return psycopg2.connect(dbname='cherkizon', **self.cfg.__dict__)
