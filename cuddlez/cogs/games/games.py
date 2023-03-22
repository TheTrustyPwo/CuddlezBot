from typing import Optional, List

import discord
from discord import app_commands
from discord.ext import commands

from cuddlez.client import CuddlezBot
from cuddlez.cogs.games.views.aki import AkinatorView


class Games(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client

    async def akinator_themes(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        choices = ["Animals", "Characters", "Objects"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    async def akinator_languages(self, interaction: discord.Interaction, current: str) -> List[
        app_commands.Choice[str]]:
        choices = ["English", "Arabic", "Chinese", "German", "Spanish", "French", "Hebrew", "Italian", "Japanese",
                   "Korean", "Dutch", "Polish", "Portugese", "Russian", "Turkish", "Indonesian"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(theme=akinator_themes)
    @app_commands.autocomplete(language=akinator_languages)
    async def akinator(self, interaction: discord.Interaction, theme: Optional[str] = None, language: Optional[str] = None):
        """
        Play akinator

        :param interaction: Interaction object
        :param theme: Theme of the Akinator
        :param language: Sets the Akinator language
        :return:
        """
        await interaction.response.defer()
        akinator = AkinatorView(user=interaction.user, theme=theme, language=language)
        await akinator.send(interaction)


async def setup(client: CuddlezBot):
    await client.add_cog(Games(client))
