import json
import logging
import pylibmc

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

        if ("x_axis_conversion" in ds
            and ds["x_axis_conversion"] not in ("date", "default")):
            logger.debug("Unknown value for "
                         "x_axis_conversion: %s" % ds["x_axis_conversion"])
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

class MemcachedStore:
    def __init__(self, servers, *args, **kwargs):
        self.mc = pylibmc.Client(servers, *args, **kwargs)

    def set(self, key, value):
        if not validate(value):
            logger.warn("Invalid data for key: %s" % key)
            return False

        return self.mc.set(key.encode("utf-8"),
                           json.dumps(value).encode("utf-8"))

    def get(self, key):
        return json.loads(self.mc[key.encode("utf-8")].decode("utf-8"))

    def __contains__(self, key):
        return key.encode("utf-8") in self.mc

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)
