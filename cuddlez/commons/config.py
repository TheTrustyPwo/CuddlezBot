from functools import reduce

import yaml


class Config:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        with open('config.yaml', 'r', encoding='utf-8') as fp:
            self._data = yaml.load(fp, Loader=yaml.FullLoader)

    def get(self, *keys):
        if len(keys) == 1:
            return self._data.get(keys[0], None)
        else:
            return reduce(lambda data, key: data[key], keys, self._data)
