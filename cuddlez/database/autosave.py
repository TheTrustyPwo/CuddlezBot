from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils, parsing


class AutoSave(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client
        self.autosave.start()

    @tasks.loop(seconds=10)
    async def autosave(self):
        await self.client.database.save_all()
        print("SAVED ALL")


async def setup(client: CuddlezBot):
    await client.add_cog(AutoSave(client))
