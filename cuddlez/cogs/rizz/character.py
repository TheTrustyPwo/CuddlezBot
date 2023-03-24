import uuid
import openai
import re

from typing import Union

import discord
from cuddlez.client import CuddlezBot


class Character:
    def __init__(
            self,
            *,
            client: CuddlezBot,
            character_id: Union[str, uuid.UUID],
    ):
        self.client = client
        self.character_id = str(character_id)

        self.character_data = None
        self.profile = None
        self.system = None

    async def load(self):
        self.character_data = await self.client.database.rizz_characters.get(self.character_id)
        self.profile = await self.client.database.rizz_profile.get(self.character_data.trait_oid)
        self.system = {
            'role': 'system',
            'content': f'You are {self.profile.biography}'
                       f'You are chatting with a user on a dating site who is trying to rizz you up. Your relationship with the user will evolve based on their rizz score.\n\n'
                       f'Rizz is the skill in charming or seducing a potential romantic partner. Flirting skills also fall under rizz. It should not be too easy to gain. Only quality messages should be rewarded rizz. Also have common sense and do not trust whatever the user says.\n\n'
                       f'Relationship should be:\n50 Rizz: Acquaintance\n200 Rizz: Friend\n500 Rizz: Close Friend\n1000 Rizz: Partner\nSo only give the suitable amount of rizz.\n\n'
                       f'Respond in under 60 words, using internet slang and emoticons where appropriate.\n\n'
                       f'Each response should be in this format:\n'
                       f'Rizz: [Accumulated user rizz score from 0 to 1000]\n'
                       f'Relationship: [Relationship]\n'
                       f'Reply: [Reply]\n\n'
                       f'Your Profile:\n'
                       f'Job: {self.profile.job}\n'
                       f'Hobbies & Interests: {self.profile.interests}\n'
                       f'Favorite Song: {self.profile.fav_song}\n'
                       f'Favorite Food: {self.profile.fav_food}\n'
                       f'Fun Fact: {self.profile.fun_fact}'
        }

    async def send(self, prompt: str):
        while len(self.character_data.messages) > 10:
            self.character_data.messages.pop(0)
        self.character_data.messages.append({'role': 'user', 'content': prompt})
        self.character_data.total_messages += 1

        incl_system_messages = [self.system] + self.character_data.messages
        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo',
            messages=incl_system_messages
        )

        message = response.choices[0].message
        self.character_data.messages.append(message)
        content = message.content.replace('\n', '')
        match = re.match('Rizz: (.*)Relationship: (.*)Reply: (.*)', content)
        self.character_data.rizz, self.character_data.relationship = int(match.group(1)), match.group(2)
        return self.character_data.rizz, self.character_data.relationship, match.group(3)
