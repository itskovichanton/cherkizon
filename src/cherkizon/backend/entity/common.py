import datetime
from dataclasses import dataclass


@dataclass
class Gitlab:
    url: str = None
    token: str = None
    api_version: int = None


@dataclass
class Namespace:
    id: int = None
    name: str = None
    gitlab: Gitlab = None
    active: bool = None


@dataclass
class Service:
    id: int = None
    created_at: datetime.datetime = None
    deleted_at: datetime.datetime = None
    description: str = None
    docs_url: str = None
    gitlab_project_id: int = None
    name: str = None
    namespace: Namespace = None
    repo: str = None
    slack_channel_id: int = None

    class Meta:
        table_name = 'service'
