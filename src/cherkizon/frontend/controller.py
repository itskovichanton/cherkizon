from src.mybootstrap_ioc_itskovichanton.ioc import bean
from src.mybootstrap_mvc_itskovichanton.pipeline import ActionRunner


@bean
class Controller:
    action_runner: ActionRunner
