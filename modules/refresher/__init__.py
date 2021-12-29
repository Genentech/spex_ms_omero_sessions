import datetime
from memcached_stats import MemcachedStats
from functools import partial
from threading import Thread
from spex_common.services.Timer import every
from spex_common.modules.cache import cache_instance
from spex_common.modules.logging import get_logger
import spex_common.modules.omeroweb as omero_web
import spex_common.modules.omero_blitz as omero_blitz


def refresher(get, get_key, host, port, logger):
    try:
        logger.info(f'connect to memcached')

        mem = MemcachedStats(host, port)
        key_prefix = get_key('')
        keys = list(filter(lambda item: item.startswith(key_prefix), set(mem.keys())))

        logger.info(f'found keys: {len(keys)}')

        for key in keys:
            value = cache_instance().get(key)

            if value is None:
                logger.info(f'Session {key} deleted before')
                continue

            active_until = getattr(value, 'active_until')

            if active_until is not None and active_until < datetime.datetime.now():
                cache_instance().delete(key)
                logger.info(f'Session {key} deleted')
                continue

            _, login = key.split(key_prefix)
            session = get(login)
            if session is None:
                cache_instance().delete(key)
                logger.info(f'Session {key} deleted')
                continue

            logger.info(f'Session {key} refreshed valid until {value.active_until}')
    except:
        logger.exception('Error refreshing sessions')
    pass


class OmeroWebRefresherWorker(Thread):
    def __init__(self, host, port, daemon=True):
        super().__init__(name=self.__class__.__name__, daemon=daemon)
        self.__logger = get_logger(self.__class__.__name__)
        self.__host = host
        self.__port = port

    def run(self):
        checker = partial(
            refresher,
            omero_web.get,
            omero_web.get_key,
            self.__host,
            self.__port,
            self.__logger
        )
        self.__logger.info(f'start checking')
        every(60, checker)


class OmeroBlitzRefresherWorker(Thread):
    def __init__(self, host, port, daemon=True):
        super().__init__(name=self.__class__.__name__, daemon=daemon)
        self.__logger = get_logger(self.__class__.__name__)
        self.__host = host
        self.__port = port

    def run(self):
        checker = partial(
            refresher,
            omero_blitz.get,
            omero_blitz.get_key,
            self.__host,
            self.__port,
            self.__logger
        )
        self.__logger.info(f'start checking')
        every(60, checker)
