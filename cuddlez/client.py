import asyncio
import logging
import logging.handlers
import os
from typing import List, Optional

import discord
import openai
from discord.ext import commands
from dotenv import load_dotenv

from database.mongodb import Database


class CuddlezBot(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            database: Database,
            testing_guild_id: Optional[int] = None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.database = database
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_disconnect(self):
        await self.database.save_all()
        print("DISCONNECTING")


async def main():
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # logger = logging.getLogger('discord')
    # logger.setLevel(logging.DEBUG)
    discord.utils.setup_logging()

    extensions = ['cogs.economy.economy', 'cogs.items.items', 'cogs.games.games', 'cogs.ai.ai', 'cogs.rizz.rizz', 'database.autosave']
    database = Database(os.getenv('MONGO_URI', ''))
    async with CuddlezBot(commands.when_mentioned, database=database, initial_extensions=extensions, testing_guild_id=1009092392026124298, intents=discord.Intents.all()) as bot:
        await bot.start(os.getenv('BOT_TOKEN', ''))


if __name__ == '__main__':
    asyncio.run(main())
