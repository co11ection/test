import logging

from asyncpg import Pool

logger = logging.getLogger(__name__)


class ContentRepository:
    def __init__(self, db: Pool):
        self._db = db
