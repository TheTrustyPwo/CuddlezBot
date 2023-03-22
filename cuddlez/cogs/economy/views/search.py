import random
from typing import List

import discord

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils
from cuddlez.commons.config import Config


class SearchButton(discord.ui.Button):
    def __init__(self, search_location: str):
        super().__init__(style=discord.ButtonStyle.primary, label=search_location)
        self.search_location = search_location

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: SearchView = self.view

        if interaction.user != view.user:
            await interaction.response.send_message(embed=utils.get_embed('notYourMenu'), ephemeral=True)
            return

        view.stop()
        for child in view.children:
            child.disabled = True

        location_data = Config().get('searchLocations', self.search_location)
        if random.random() <= location_data['successChance'] / 100:
            earnings = random.randint(location_data['minEarnings'], location_data['maxEarnings'])
            message = location_data['successMessage'].replace('{amount}', '{:,}'.format(earnings))
            embed = utils.get_embed('searchSuccess', user=view.user.name, location=self.search_location, message=message)
            await view.give_earnings(earnings)
            await interaction.response.edit_message(embed=embed, view=view)
        elif random.random() <= location_data['deathChance'] / 100:
            message = location_data['deathMessage']
            embed = utils.get_embed('searchFailed', user=view.user.name, location=self.search_location, message=message)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            message = location_data['failMessage']
            embed = utils.get_embed('searchFailed', user=view.user.name, location=self.search_location, message=message)
            await interaction.response.edit_message(embed=embed, view=view)


class SearchView(discord.ui.View):
    def __init__(
            self,
            *,
            client: CuddlezBot,
            user: discord.User,
            search_locations: List[str] = None,
            num_choices: int = 3,
            timeout: float = 30.0
    ):
        super().__init__(timeout=timeout)
        self.client = client
        self.user = user
        self.search_locations = search_locations
        self.num_choices = num_choices

        if self.search_locations is None:
            all_locations = list(Config().get('searchLocations').keys())
            self.search_locations = random.sample(all_locations, self.num_choices)

        for location in self.search_locations:
            self.add_item(SearchButton(location))

    async def give_earnings(self, amount: int):
        data = await self.client.database.users.get(self.user.id)
        data.wallet += amount
