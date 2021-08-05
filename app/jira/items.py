from datetime import datetime
from logging import Logger
from apscheduler.job import Job
from attlasian import Attlasian
from attlasian.types import Issue, DevStatus, JiraAccount, JiraStatus
from json import loads
from app.scheduler import Scheduler
from flask import current_app


class WaitingItem:
    __issue: Issue = None
    __devStatus: DevStatus = None
    __job: Job = None

    def __init__(self, data) -> None:
        self.__issue = Issue(loads(data))
        self.__job = Scheduler.get_job(self.__issue.key)

    @property
    def issue(self) -> Issue:
        return self.__issue

    @property
    def key(self):
        return self.__issue.key

    @property
    def summary(self):
        return self.__issue.summary

    @property
    def assignee(self) -> JiraAccount:
        return self.__issue.assignee

    @property
    def status(self):
        return self.__issue.status.name

    @property
    def job(self) -> Job:
        return self.__job

    @job.setter
    def job(self, job):
        self.__job = job

    @property
    def isValid(self) -> bool:
        self.sync()
        return not self.errors

    @property
    def returnTo(self) -> JiraAccount:
        return Attlasian.Jira.getReturnTo(self.key)

    @property
    def errors(self):
        errors = []
        with Scheduler.app_context as context:
            config = context.app.config
            my_username = config.get("JIRA_USERNAME")
            if self.returnTo.email == my_username:
                Scheduler.logger.warn(f"{self.key} is not valid, self assigned problem")
                errors.append("Self assigned for review")
            if self.assignee.email != my_username:
                Scheduler.logger.warn(
                    f"{self.key} is not valid, not assigned to reviewer"
                )
                errors.append("Not proper assignment")
            if self.status != JiraStatus.CODE_REVIEW.value:
                Scheduler.logger.warn(
                    f"{self.key} is not valid, not Code Review status"
                )
                errors.append("Not in the right status")
        return errors

    @property
    def devStatus(self) -> DevStatus:
        if not self.__devStatus:
            self.__devStatus = Attlasian.Jira.getDevStatus(self.__issue)
        return self.__devStatus

    def sync(self):
        logger: Logger = current_app.logger
        logger.info(f"Syncing issue {self.key}")
        self.__issue = Attlasian.Jira.getIssue(self.key)


class ProcessedItem:
    __issue: Issue = None
    __processed: dict = None

    def __init__(self, data):
        json = loads(data)
        self.__issue = Issue(json)
        self.__processed = json.get("processed")

    @property
    def issue(self) -> Issue:
        return self.__issue

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.__processed.get("timestamp"))

    @property
    def result(self) -> bool:
        return self.__processed.get("result")

    @property
    def error(self):
        return self.__processed.get("error")
