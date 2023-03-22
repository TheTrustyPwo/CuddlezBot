from typing import Optional

import os
import discord
from discord import app_commands
from discord.ext import commands

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils, parsing


class Admin(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client

    @app_commands.command()
    async def evaluate(self, interaction: discord.Interaction, code: str):
        """
        Evaluate a piece of code, PLEASE DON"T DO BAD STUFF TO ME PC

        :param interaction: Interaction object
        :param code: Code to evaluate
        :return:
        """
        result = eval(code)
        await interaction.response.send_message(result)


async def setup(client: CuddlezBot):
    await client.add_cog(Admin(client))
