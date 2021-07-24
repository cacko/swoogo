from logging import Logger, log


class Remote(object):

    _instance = None
    _config = {}
    _connector = None
    _api = None
    _logger: Logger = None

    def __new__(cls, config: dict, logger, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config: dict, logger, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._config = config
        self._logger = logger
        self._api = self._connector(**config)
