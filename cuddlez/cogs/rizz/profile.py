import re
import uuid

import openai

from cuddlez.database.modals.base import Base
from typing import Union, Mapping
import copy

DEFAULT_SYSTEM_MESSAGE = {
    'role': 'system',
    'content': 'Generate a random unique profile of a girl on an online chatting app with the following attributes.'
               ''
               'Bio: I am [name] and [description]'
               'Job:'
               'Hobbies & Interests:'
               'Favorite Song:'
               'Favorite Food:'
               'Fun Fact:'
}

CUSTOM_SYSTEM_MESSAGE = {
    'role': 'system',
    'content': 'Generate a profile of a girl on an online chatting app based on the user description with the following attributes.'
               ''
               'The user description is {user_description}'
               'Follow the user description with some variations, but still abide by the response format below:'
               ''
               'Bio: I am [name] and [description]'
               'Job:'
               'Hobbies & Interests:'
               'Favorite Song:'
               'Favorite Food:'
               'Fun Fact:'
}


class CharacterProfile(Base):
    def __init__(
            self,
            *,
            oid: Union[str, uuid.UUID],
            biography: str,
            job: str,
            interests: str,
            fav_song: str,
            fav_food: str,
            fun_fact: str
    ):
        self.oid = str(oid)
        self.biography = biography
        self.job = job
        self.interests = interests
        self.fav_song = fav_song
        self.fav_food = fav_food
        self.fun_fact = fun_fact

        if self.biography is not None:
            self.name = self.biography.split()[0]

    @staticmethod
    async def generate(custom_description: str = None):
        system = DEFAULT_SYSTEM_MESSAGE
        if custom_description is not None:
            system = copy.deepcopy(CUSTOM_SYSTEM_MESSAGE)
            system['content'] = system['content'].replace('{user_description}', custom_description)

        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo',
            messages=[system]
        )

        content = response.choices[0].message.content.replace('\n', '')
        print(content)
        match = re.match('(?:Bio|Description): (.*)Job: (.*)Hobbies & Interests: (.*)Favorite Song: (.*)Favorite Food: (.*)Fun Fact: (.*)', content)
        bio, job, interests, song, food, fact = match.groups()
        return CharacterProfile(oid=str(uuid.uuid4()), biography=bio[5:], job=job, interests=interests, fav_song=song,
                                fav_food=food, fun_fact=fact)

    def to_dict(self) -> dict:
        return {
            '_id': str(self.oid),
            'biography': self.biography,
            'job': self.job,
            'interests': self.interests,
            'favSong': self.fav_song,
            'favFood': self.fav_food,
            'funFact': self.fun_fact
        }

    @classmethod
    def from_dict(cls, data: Union[dict, Mapping[str, any]]):
        return CharacterProfile(oid=uuid.UUID(data['_id']), biography=data['biography'], job=data['job'],
                                interests=data['interests'], fav_song=data['favSong'], fav_food=data['favFood'],
                                fun_fact=data['funFact'])
