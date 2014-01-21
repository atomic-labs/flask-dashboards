import logging

logger = logging.getLogger(__name__)

def validate(data_set):
    if not isinstance(data_set, list):
        logger.debug("Data set must be a list")
        return False

    for ds in data_set:
        if not isinstance(ds, dict):
            logger.debug("Data set must be a list of dicts")
            return False

        if "key" not in ds:
            logger.debug("Missing required attribute: key")
            return False

        if "values" not in ds:
            logger.debug("Missing required attribute: values")
            return False

    return True

class SimpleStore:
    def __init__(self):
        self._store = {}

    def set(self, key, value):
        if not validate(value):
            logger.warn("Invalid data for key: %s" % key)
            return False

        self._store[key] = value
        return True

    def get(self, key):
        return self._store[key]

    def __contains__(self, key):
        return key in self._store

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)
