from logging import Logger
from flask import Flask
from flask.ctx import AppContext
from flask_apscheduler import APScheduler
from redis import StrictRedis


class StorageMeta(type):
    pass


class Storage(object, metaclass=StorageMeta):

    _redis: StrictRedis = None
    _instance = None

    def __init__(self, app) -> None:
        redis_client = StrictRedis()
        self._redis = redis_client.from_url(app.config.get("REDIS_URL"))

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
    def keys(cls, pattern):
        return cls._instance._redis.keys(pattern)

    @classmethod
    def mget(cls, keys, *args) -> list:
        return cls._instance._redis.mget(keys, *args)

    @classmethod
    def get(cls, name):
        return cls._instance._redis.get(name)

    @classmethod
    def set(cls, name, value, *args, **kwargs):
        return cls._instance._redis.set(name, value, *args, **kwargs)

    @classmethod
    def rename(cls, src, dst):
        return cls._instance._redis.rename(src, dst)

    @classmethod
    def persist(cls, name):
        return cls._instance._redis.persist(name)
