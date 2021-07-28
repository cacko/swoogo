import logging
from .types import Commit
from .remote import Remote
from atlassian import Bitbucket
from .types import Commit
import requests

ENDPOINT_APPROVE = '/2.0/repositories/swoogo/www.swoogo.com/commit/{commit.id}/approve'

class bitbucket_(Remote):

    _connector = Bitbucket

    def approve(self, commits: list[Commit]):
        for commit in commits:
            try:
                self._api.post( ENDPOINT_APPROVE.format(commit=commit), {
                    "hasComments": False
                })
                self._logger.info(f"\tapproved {commit.id} ")
            except requests.exceptions.HTTPError as err:
                self._logger.error(err)
                pass
