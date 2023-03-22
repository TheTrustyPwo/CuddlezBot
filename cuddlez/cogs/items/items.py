from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils, parsing
from cuddlez.cogs.items.views.inventory import InventoryView


class Items(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client

    @app_commands.command()
    async def inventory(self, interaction: discord.Interaction, target: Optional[discord.User] = None):
        """
        Check someone's inventory

        :param interaction: Interaction object
        :param target: User to check inventory
        :return:
        """
        target = target or interaction.user
        inventory = InventoryView(client=self.client, user=target)
        await inventory.send(interaction)


async def setup(client: CuddlezBot):
    await client.add_cog(Items(client))
