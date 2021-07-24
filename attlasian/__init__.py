from flask.app import Flask
from werkzeug.exceptions import UnprocessableEntity
from .jira import jira_
from .bitbucket import bitbucket_
class AttlasianMeta(type):
    @property
    def Jira(cls) -> jira_:
        if not cls._instance:
            raise UnprocessableEntity
        return cls._instance.jira

    @property
    def Bitbucket(cls) -> bitbucket_: 
        if not cls._instance:
            raise UnprocessableEntity
        return cls._instance.bitbucket      

class Attlasian(object, metaclass=AttlasianMeta):

    __jira: jira_ = None
    __bitbucket: bitbucket_ = None
    __app: Flask = None
    _instance = None

    def __init__(self, app) -> None:
        self.__app = app

    def __new__(cls, app: Flask, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def register(cls, app: Flask):
        if not cls._instance:
            cls._instance = cls(app)
        return cls._instance

    @property
    def jira(self) -> jira_:
        if not self.__jira:
            self.__jira = jira_(self.namespace(jira_), self.__app.logger)
        return self.__jira

    @property
    def bitbucket(self) -> bitbucket_:
        if not self.__bitbucket:
            self.__bitbucket = bitbucket_(self.namespace(bitbucket_), self.__app.logger)
        return self.__bitbucket

    def namespace(self, cls):
        ns = cls.__qualname__.upper()
        return self.__app.config.get_namespace(ns)