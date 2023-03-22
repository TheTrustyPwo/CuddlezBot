from typing import Union, Mapping


class Base:
    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Union[dict, Mapping[str, any]]):
        raise NotImplementedError
