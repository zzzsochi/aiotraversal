import asyncio
from abc import ABCMeta, abstractmethod


class AbstractResource(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, name):
        """ Return traverser instance

        In simple:

            return traversal.Traverser(self, [name])
        """

    @asyncio.coroutine
    @abstractmethod
    def __getchild__(self, name):
        """ Return child resource or None, if not exists """


class AbstractView(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, resource):
        """ Receive current traversed resource """

    @asyncio.coroutine
    @abstractmethod
    def __call__(self):
        """ Return aiohttp.web.Response """
