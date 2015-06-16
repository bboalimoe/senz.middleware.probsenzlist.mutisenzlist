"""Provide log for other modules"""

from logentries import LogentriesHandler
import logging
from config import LOGENTRIES_TOKEN

__all__ = ['logger']

logger = logging.getLogger('logentries')
logger.setLevel(logging.INFO)
test = LogentriesHandler(LOGENTRIES_TOKEN)

logger.addHandler(test)

logger.info("[probsenzlist.mutisenzlist] Log start...")
