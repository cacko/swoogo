from logging import Logger
from types import ClassMethodDescriptorType
from apscheduler.jobstores.redis import RedisJobStore
from flask import Flask
from flask.ctx import AppContext
from flask_apscheduler import APScheduler
from urllib.parse import urlparse


class SchedulerMeta(type):
    @property
    def logger(cls) -> Logger:
        return cls._instance.app_context.app.logger

    @property
    def app_context(cls) -> AppContext:
        return cls._instance._scheduler.app.app_context()


class Scheduler(object, metaclass=SchedulerMeta):

    _scheduler: APScheduler = None
    _instance = None

    def __init__(self, app) -> None:
        self._scheduler = APScheduler()
        self._scheduler.init_app(app)
        p = urlparse(app.config.get("REDIS_URL"))
        jobstores = {"default": RedisJobStore(host=p.netloc, db=p.path.strip("/"))}
        self._scheduler.scheduler.configure(jobstores=jobstores)

    def __new__(cls, app: Flask, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def register(cls, app: Flask):
        if not cls._instance:
            cls._instance = cls(app)
        return cls._instance

    @classmethod
    def start(cls):
        cls._instance._scheduler.start()

    @classmethod
    def add_job(cls, *args, **kwargs):
        return cls._instance._scheduler.add_job(*args, **kwargs)

    @classmethod
    def get_job(cls, id, jobstore=None):
        return cls._instance._scheduler.get_job(id, jobstore)

    @classmethod
    def cancel_jobs(cls, id, jobstore=None):
        return cls._instance._scheduler.remove_job(id, jobstore)

    @property
    def logger(self) -> Logger:
        return self.app_context.app.logger

    @property
    def app_context(self) -> AppContext:
        return self._scheduler.app.app_context()
