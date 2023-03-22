import uuid
from typing import Union, Mapping

from cuddlez.database.modals.base import Base

DEFAULT_SYSTEM_MESSAGE = ''


class CharacterData(Base):
    def __init__(
            self,
            *,
            oid: Union[uuid.UUID, str] = None,
            user_id: Union[int, str],
            trait_oid: Union[uuid.UUID, str],
            rizz: int = 0,
            relationship: str = None,
            messages: list = None,
            total_messages: int = 0
    ):
        self.oid = str(uuid.uuid4()) if oid is None else str(oid)
        self.user_id = str(user_id)
        self.trait_oid = str(trait_oid)
        self.rizz = rizz
        self.relationship = relationship or 'Stranger'
        self.messages = messages or []
        self.total_messages = total_messages

    def to_dict(self) -> dict:
        return {
            '_id': self.oid,
            'user_id': self.user_id,
            'profile': self.trait_oid,
            'rizz': self.rizz,
            'relationship': self.relationship,
            'messages': self.messages,
            'total_messages': self.total_messages
        }

    @classmethod
    def from_dict(cls, data: Union[dict, Mapping[str, any]]):
        oid, user_id, profile = data['_id'], data['user_id'], data['profile']
        rizz, relationship, messages = int(data['rizz']), data['relationship'], data['messages']
        total = data['total_messages'] if 'total_messages' in data else 0
        return CharacterData(oid=oid, user_id=user_id, trait_oid=profile, rizz=rizz, relationship=relationship,
                             messages=messages, total_messages=total)
