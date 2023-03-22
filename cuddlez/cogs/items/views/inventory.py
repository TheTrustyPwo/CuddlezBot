import discord

from typing import Union
from cuddlez.database.modals.user import Item
from cuddlez.commons.paginator import Paginator
from cuddlez.client import CuddlezBot


class InventoryView(discord.ui.View):
    def __init__(
            self,
            *,
            client: CuddlezBot,
            user: discord.User,
            items_per_page: int = 8,
            separator: str = '\n\n',
            timeout: float = 30.0
    ):
        super().__init__(timeout=timeout)
        self.client = client
        self.user = user
        self.items_per_page = items_per_page
        self.separator = separator

        self.current_page = 1
        self.max_page = 1

    async def send(self, interaction: discord.Interaction) -> None:
        self.update_buttons()
        await interaction.response.send_message(embed=await self.create_embed(), view=self)

    async def update_message(self, interaction: discord.Interaction) -> None:
        self.update_buttons()
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_buttons(self) -> None:
        self.first_page.disabled = self.current_page == 1
        self.prev_page.disabled = self.current_page == 1
        self.last_page.disabled = self.current_page == self.max_page
        self.next_page.disabled = self.current_page == self.max_page

    @staticmethod
    def parse_item(item: Item) -> str:
        return f'{item.item_id} - {item.amount}'

    async def create_embed(self) -> discord.Embed:
        until_item = self.current_page * self.items_per_page
        from_item = until_item - self.items_per_page
        user_data = await self.client.database.users.get(self.user.id)
        display_items = map(lambda v: self.parse_item(v), user_data.inventory[from_item:until_item])
        self.max_page = int(len(user_data.inventory) / self.items_per_page) + 1

        embed = discord.Embed(title=f"{self.user.name}'s Inventory")
        embed.description = self.separator.join(display_items)
        return embed

    @discord.ui.button(label='≪', style=discord.ButtonStyle.primary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        await self.update_message(interaction)

    @discord.ui.button(label='≫', style=discord.ButtonStyle.primary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.max_page
        await self.update_message(interaction)
