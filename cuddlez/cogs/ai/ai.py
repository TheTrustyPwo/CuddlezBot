import random
from typing import Optional, List

import discord
import openai
from discord import app_commands
from discord.ext import commands
from textblob import TextBlob

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils
from cuddlez.cogs.ai.views.adventure import AdventureView
from cuddlez.cogs.ai.mbti import MBTIGuesser


class AI(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client

    @commands.Cog.listener(name='on_message')
    async def encourage(self, message):
        blob = TextBlob(message.content)
        sentiment = blob.sentiment.polarity
        if message.author == self.client.user or sentiment >= 0 or random.random() > 0.2:
            return

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Give encouraging message to prompt"},
                {"role": "user", "content": message.content},
            ]
        ).choices[0].message.content
        await message.reply(response)

    async def adventure_types(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        choices = ["Normal", "Sexual", "Scary"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(type=adventure_types)
    async def adventure(self, interaction: discord.Interaction, type: Optional[str] = None, prompt: Optional[str] = None):
        """
        Play Choose Your Own Adventure styled game

        :param interaction: Interaction object
        :param type: Type of adventure story
        :param prompt: Starting prompt of the story
        :return:
        """
        adventure_view = AdventureView(user=interaction.user, type=type, starting_prompt=prompt)
        await adventure_view.start(interaction)

    @app_commands.command()
    async def analogy(self, interaction: discord.Interaction, source: str, target: str):
        """
        Create an analogy between 2 objects

        :param interaction: Interaction object
        :param source: Source object
        :param target: Target object
        :return:
        """
        await interaction.response.defer()
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
                {"role": "system", "content": "Create an analogy for this phrase:"},
                {"role": "user", "content": f"{source} are {target} in that:"},
            ]
        )
        content = response.choices[0].message.content
        embed = utils.get_embed('analogy', user=interaction.user, source=source, target=target, content=content)
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    async def mbti(self, interaction: discord.Interaction):
        """
        Cuddlez with try to guess your MBTI type!

        :param interaction: Interaction object
        :return:
        """
        mbti_guesser = MBTIGuesser(client=self.client, user=interaction.user)
        await mbti_guesser.start(interaction)


async def setup(client: CuddlezBot):
    await client.add_cog(AI(client))
    # from cuddlez.cogs.ai.rizz.profile import CharacterProfile
    # from cuddlez.cogs.ai.rizz.character_data import CharacterData
    # openai.api_key = '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'
    # trait = CharacterProfile.generate()
    # await client.database.save_rizz_profile(trait)
    # print("SAVED RIZZ PROFILE")
    # character = CharacterData(trait_oid=trait.oid, user_id=759285370662682644)
    # await client.database.save_rizz_character(character)
    # print("SAVED CHARACTER")
    # user = await client.database.get_user(759285370662682644)
    # user.rizzing = character.oid
    # await client.database.save_user(user)
    # print("DONE")
