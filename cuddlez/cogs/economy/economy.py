from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils, parsing
from cuddlez.cogs.economy.views.search import SearchView


class Economy(commands.Cog):
    def __init__(self, client: CuddlezBot):
        self.client = client

    @app_commands.command()
    async def balance(self, interaction: discord.Interaction, target: Optional[discord.User] = None):
        """
        Check someone's balance

        :param interaction: Interaction object
        :param target: User to check balance
        :return:
        """
        target = target or interaction.user
        data = await self.client.database.users.get(target.id)
        embed = utils.get_embed('balance', user=target.name, wallet=data.wallet, bank=data.bank, test=target)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def deposit(self, interaction: discord.Interaction, amount: str):
        """
        Deposit money into your bank

        :param interaction: Interaction object
        :param amount: Amount to deposit
        :return:
        """
        data = await self.client.database.users.get(interaction.user.id)
        amount = parsing.parse_number(amount, data.wallet)
        if amount is None or amount <= 0:
            await interaction.response.send_message(embed=utils.get_embed('invalidNumber'))
            return
        if data.wallet < amount:
            await interaction.response.send_message(embed=utils.get_embed('notEnoughMoney', required=amount))
            return
        data.wallet -= amount
        data.bank += amount
        embed = utils.get_embed('deposit', wallet=data.wallet, bank=data.bank)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        """
        Withdraw money into your wallet

        :param interaction: Interaction object
        :param amount: Amount to withdraw
        :return:
        """
        data = await self.client.database.get_user(interaction.user.id)
        amount = parsing.parse_number(amount, data.wallet)
        if amount is None or amount <= 0:
            await interaction.response.send_message(embed=utils.get_embed('invalidNumber'))
            return
        if data.bank < amount:
            await interaction.response.send_message(embed=utils.get_embed('notEnoughMoney', required=amount))
            return
        data.bank -= amount
        data.wallet += amount
        embed = utils.get_embed('withdraw', wallet=data.wallet, bank=data.bank)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def pay(self, interaction: discord.Interaction, target: discord.User, amount: str):
        """
        Send money to another user quickly

        :param interaction: Interaction object
        :param target: User to send money to
        :param amount: Amount of money to send
        :return:
        """
        user_data = await self.client.database.users.get(interaction.user.id)
        amount = parsing.parse_number(amount, user_data.wallet)
        if amount is None or amount <= 0:
            await interaction.response.send_message(embed=utils.get_embed('invalidNumber'))
            return
        if user_data.wallet < amount:
            await interaction.response.send_message(embed=utils.get_embed('notEnoughMoney', required=amount))
            return
        target_data = await self.client.database.users.get(target.id)
        user_data.wallet -= amount
        target_data.wallet += amount
        embed = utils.get_embed('pay', amount=amount, receiver=target.name, sender_wallet=user_data.wallet,
                                 receiver_wallet=target_data.wallet)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def search(self, interaction: discord.Interaction):
        """
        Search various places for money, with some risks

        :param interaction: Interaction object
        :return:
        """
        view = SearchView(client=self.client, user=interaction.user)
        await interaction.response.send_message(embed=utils.get_embed('search'), view=view)


async def setup(client: CuddlezBot):
    await client.add_cog(Economy(client))
