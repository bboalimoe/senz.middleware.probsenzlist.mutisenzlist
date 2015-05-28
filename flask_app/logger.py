"""Provide log for other modules"""

from logentries import LogentriesHandler
import logging
import time

__all__ = ['logger']

logger = logging.getLogger('logentries')
logger.setLevel(logging.INFO)
LOGENTRIES_TOKEN = '188e1812-12aa-4de0-83ea-9aa9a7bd807a'
test = LogentriesHandler(LOGENTRIES_TOKEN)

logger.addHandler(test)

logger.info("[probsenzlist.mutisenzlist] Log start...")
