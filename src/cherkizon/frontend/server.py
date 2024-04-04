import uvicorn
from fastapi import FastAPI
from src.mbulak_tools.apis.hc.frontend.support import HealthcheckFastAPISupport
from src.mybootstrap_core_itskovichanton.logger import LoggerService
from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_ioc_itskovichanton.utils import default_dataclass_field
from src.mybootstrap_mvc_fastapi_itskovichanton.error_handler import ErrorHandlerFastAPISupport
from src.mybootstrap_mvc_fastapi_itskovichanton.middleware_logging import HTTPLoggingMiddleware
from src.mybootstrap_mvc_fastapi_itskovichanton.presenters import JSONResultPresenterImpl
from src.mybootstrap_mvc_itskovichanton.result_presenter import ResultPresenter
from starlette.requests import Request

from src.cherkizon.backend.entity.common import Deploy
from src.cherkizon.frontend.controller import Controller


@bean(port=("server.port", int, 8082), host=("server.host", str, "0.0.0.0"))
class Server:
    error_handler_fast_api_support: ErrorHandlerFastAPISupport
    healthcheck_support: HealthcheckFastAPISupport
    presenter: ResultPresenter = default_dataclass_field(JSONResultPresenterImpl(exclude_unset=True))
    controller: Controller
    logger_service: LoggerService

    def init(self, **kwargs):
        self.fast_api = self.init_fast_api()
        self.add_routes()

    def start(self):
        uvicorn.run(self.fast_api, port=self.port, host=self.host)

    def init_fast_api(self) -> FastAPI:
        r = FastAPI(title='cherkizon', debug=False)
        self.error_handler_fast_api_support.mount(r)
        self.healthcheck_support.mount(r)
        r.add_middleware(HTTPLoggingMiddleware, encoding="utf-8", logger=self.logger_service.get_file_logger("http"))
        return r

    def add_routes(self):
        @self.fast_api.post("/deploy/register")
        async def register_deploy(request: Request, deploy: Deploy):
            return self.presenter.present(await self.controller.register_deploy(deploy))

        @self.fast_api.post("/deploy/list")
        async def list_deploys(request: Request, filter: Deploy):
            return self.presenter.present(await self.controller.list_deploys(filter))

        @self.fast_api.post("/deploy/restart")
        async def restart_deploy(request: Request, deploy: Deploy):
            return self.presenter.present(await self.controller.execute_action_on_deploy(deploy, action="restart"))

        @self.fast_api.post("/deploy/stop")
        async def stop_deploy(request: Request, deploy: Deploy):
            return self.presenter.present(await self.controller.execute_action_on_deploy(deploy, action="stop"))
