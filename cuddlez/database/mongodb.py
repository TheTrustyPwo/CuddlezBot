import uuid
from typing import Union, Type

import motor.core
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne

from cuddlez.cogs.rizz.character_data import CharacterData
from cuddlez.cogs.rizz.profile import CharacterProfile
from cuddlez.database.modals.base import Base
from cuddlez.database.modals.user import CuddlezUser


class Database:
    def __init__(self, uri: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client['cuddlez']

        self.users = UserCache(database=self)
        self.rizz_profile = RizzProfileCache(database=self)
        self.rizz_characters = RizzCharactersCache(database=self)

    async def save_all(self):
        await self.users.save_all()
        await self.rizz_profile.save_all()
        await self.rizz_characters.save_all()

    async def get_user_characters(self, user_id: Union[str, int]) -> list[CharacterData]:
        user_id = str(user_id)
        characters = []
        async for data in self.db.characters.find({'user_id': user_id}):
            characters.append(CharacterData.from_dict(data))
        return characters


class Cache:
    def __init__(
            self,
            *,
            database: Database,
            coll_name: str,
            key_type: type = str,
            value_type: type = Type[Base],
            max_items: int = 100
    ):
        self.database = database
        self.coll_name = coll_name
        self.key_type = key_type
        self.value_type = value_type
        self.max_items = max_items

        self._coll: motor.core.Collection = self.database.db[self.coll_name]
        self._data = {}

    def is_cached(self, key):
        return key in self._data

    async def get(self, key):
        if self.is_cached(key):
            return self._data[key]

        data = await self._coll.find_one({'_id': key})
        if data is None:
            return None

        self.set(key, self.value_type.from_dict(data))
        return self._data[key]

    def set(self, key, value):
        self._data[key] = value

    async def delete(self, key):
        self._data.pop(key)
        self._coll.delete_one({'_id': key})

    async def save(self, key, value=None):
        if value is None and not self.is_cached(key):
            raise RuntimeError
        value = value or self._data[key]
        self._coll.update_one({'_id': key}, {'$set': value.to_dict()}, upsert=True)

    async def save_all(self):
        operations = [UpdateOne({'_id': key}, {'$set': value.to_dict()}, upsert=True) for key, value in
                      self._data.items()]
        if len(operations) > 0:
            await self._coll.bulk_write(operations)


class UserCache(Cache):
    def __init__(
            self,
            *,
            database: Database
    ):
        super().__init__(database=database, coll_name='users', key_type=str, value_type=CuddlezUser)

    async def get(self, user_id):
        user_id = str(user_id)
        if self.is_cached(user_id):
            return self._data[user_id]

        user_data = await self._coll.find_one({'_id': user_id})
        if user_data is None:
            return CuddlezUser(user_id=user_id)

        self.set(user_id, CuddlezUser.from_dict(user_data))
        return self._data[user_id]


class RizzProfileCache(Cache):
    def __init__(
            self,
            *,
            database: Database
    ):
        super().__init__(database=database, coll_name='rizz', key_type=str, value_type=CharacterProfile)


class RizzCharactersCache(Cache):
    def __init__(
            self,
            *,
            database: Database
    ):
        super().__init__(database=database, coll_name='characters', key_type=str, value_type=CharacterData)
