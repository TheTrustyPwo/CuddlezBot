from typing import Optional

import discord
import openai.error
from discord import app_commands
from discord.ext import commands

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils, parsing
from cuddlez.cogs.rizz.views.menu import RizzMainMenu
from cuddlez.cogs.rizz.character import Character
from cuddlez.cogs.rizz.modals.character_creator import CharacterCreator


class Rizz(commands.GroupCog):
    def __init__(self, client: CuddlezBot):
        self.client = client
        self.processing: set[int] = set()

    @commands.Cog.listener(name='on_message')
    async def rizz_chat(self, message: discord.Message):
        if message.author.id == 1052794290037866496 or message.channel.id != 1087287913202593896 or message.content.startswith('.'):
            return

        if message.author.id in self.processing:
            await message.reply('Please wait until the AI has replied to your previous message before sending another one.')
            return

        async with message.channel.typing():
            self.processing.add(message.author.id)
            user_data = await self.client.database.users.get(message.author.id)
            if user_data.rizzing is None:
                return

            character = Character(client=self.client, character_id=user_data.rizzing)
            await character.load()

            prev_rizz = character.character_data.rizz
            try:
                rizz, relationship, reply = await character.send(message.content)
            except Exception as e:
                await message.reply(f'An unexpected error occurred while processing this message. Please resend it. {e}')
                self.processing.remove(message.author.id)
                return

        await message.reply(f'`@{character.profile.name}:` {reply}\n'
                            f'> **Rizz:** {rizz} `{"+" if rizz >= prev_rizz else ""}{rizz - prev_rizz}`\n'
                            f'> **Relationship:** {relationship}')
        if rizz >= 1000:
            standing = character.profile.update_leaderboard(message.author.id, character.character_data.total_messages)
            await message.reply(f'YOU HAVE RIZZED DIS GIRL WITH {character.character_data.total_messages} messages AND IS LEADERBOARD #{standing}')
        self.processing.remove(message.author.id)

    @app_commands.command()
    async def menu(self, interaction: discord.Interaction):
        """
        Access the Main Menu for Rizz

        :param interaction: Interaction object
        :return:
        """
        menu = RizzMainMenu(client=self.client, user=interaction.user)
        await menu.send(interaction)

    @app_commands.command()
    async def create(self, interaction: discord.Interaction):
        """
        Generate a new character from your own description

        :param interaction:
        :return:
        """
        await interaction.response.send_modal(CharacterCreator(client=self.client, user=interaction.user))


async def setup(client: CuddlezBot):
    await client.add_cog(Rizz(client))
