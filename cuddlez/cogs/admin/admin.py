from typing import Optional

import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils, parsing
from cuddlez.commons.config import Config


class Admin(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client

    @app_commands.command()
    async def evaluate(self, interaction: discord.Interaction, code: str):
        """
        Evaluate a piece of code, PLEASE DON'T DO BAD STUFF TO ME PC

        :param interaction: Interaction object
        :param code: Code to evaluate
        :return:
        """
        if interaction.user.id not in Config().get('adminIDs'):
            await interaction.response.send_message("FUF OFF DIS NOT 4 U")
            return

        if '\\' in code or 'rmdir' in code:
            await interaction.response.send_message("GO AWAY")
            return

        try:
            result = eval(code)
            await interaction.response.send_message(result)
        except Exception as e:
            await interaction.response.send_message(f'{e}')


async def setup(client: CuddlezBot):
    await client.add_cog(Admin(client))
