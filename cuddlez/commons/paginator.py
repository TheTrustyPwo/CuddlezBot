from typing import List

import discord


class Paginator(discord.ui.View):
    def __init__(
            self,
            *,
            items: List[object],
            items_per_page: int = 8,
            separator: str = '\n\n',
            timeout: float = 30.0
    ):
        super().__init__(timeout=timeout)
        self.items = items
        self.items_per_page = items_per_page
        self.separator = separator

        self.current_page = 1
        self.max_page = int(len(self.items) / self.items_per_page) + 1

    async def send(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.create_embed(), view=self)

    def update_buttons(self) -> None:
        self.first_page.disabled = self.current_page == 1
        self.prev_page.disabled = self.current_page == 1
        self.last_page.disabled = self.current_page == self.max_page
        self.next_page.disabled = self.current_page == self.max_page

    def create_embed(self) -> discord.Embed:
        embed = discord.Embed(title='test')
        until_item = self.current_page * self.items_per_page
        from_item = until_item - self.items_per_page
        display_items = map(str, self.items[from_item:until_item])
        embed.description = self.separator.join(display_items)
        return embed

    @discord.ui.button(label='≪', style=discord.ButtonStyle.primary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label='≫', style=discord.ButtonStyle.primary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.max_page
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)
