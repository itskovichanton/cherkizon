import re
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from typing import Protocol

from src.mybootstrap_core_itskovichanton.utils import calc_parallel, execute_parallel
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.exceptions import CoreException, \
    ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND

from src.cherkizon.backend.apis.agent import Agent
from src.cherkizon.backend.entity.common import Machine, Deploy
from src.cherkizon.backend.usecase.list_deploys import ListDeploysUseCase
from src.cherkizon.backend.usecase.list_machines import ListMachinesUseCase


def _extract_url_params(s):
    params = {}
    matches = re.findall(r'\[(.*?)]', s)
    if matches:
        params_list = [p.strip() for p in matches[0].split(',')]
        for param in params_list:
            key, value = param.split('=')
            params[key] = value
    return params


def _extract_service_name(s):
    return s[s.index("//") + 2:s.index("[")]


class GetDeployUrlUseCase(Protocol):

    def get_deploy_url(self, deploy: Deploy) -> str:
        ...

    def compile_url(self, url: str, protocol=None) -> str:
        ...


@bean
class GetDeployUrlUseCaseImpl(GetDeployUrlUseCase):
    list_deploys_uc: ListDeploysUseCase

    def get_deploy_url(self, deploy: Deploy, protocol=None) -> str:

        if not (deploy.machine and deploy.replica and deploy.deploy.port):
            deploys = self.list_deploys_uc.find(deploy, with_machines=False).deploys
            if len(deploys) == 0:
                raise CoreException(message="деплой не найден", reason=ERR_REASON_SERVER_RESPONDED_WITH_ERROR_NOT_FOUND)
            deploy = deploys[0]

        if not (deploy.replica and deploy.deploy.port):
            raise CoreException(message="порт деплоя не отвечает")

        return deploy.get_url(protocol)

    def compile_url(self, url: str, protocol=None) -> str:
        if url.startswith("eureka"):
            url_params = _extract_url_params(url)
            url_tail = url[url.index("]/") + 1:]
            url_host = self.get_deploy_url(deploy=Deploy(service=_extract_service_name(url),
                                                         version=url_params.get("version") or "master",
                                                         env=url_params.get("env") or "dev"), protocol=protocol)
            url = url_host + url_tail
        return url

        # eureka://reports[secure=false, env=dev, version=master]/find_report?task_id=232332
