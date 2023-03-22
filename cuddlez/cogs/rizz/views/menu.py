import discord

from cuddlez.client import CuddlezBot
from cuddlez.cogs.rizz.modals import CharacterCreator
from cuddlez.utils import utils

CHARACTER_EMOJIS = {
    'Stranger': '🕵',
    'Acquaintance': '👋',
    'Friend': '😊',
    'Close Friend': '💛',
    'Partner': '💕'
}


class DynamicRizzMenu(discord.ui.View):
    def __init__(
            self,
            client: CuddlezBot,
            user: discord.User,
            timeout: float = 300.0
    ):
        super().__init__(timeout=timeout)
        self.client = client
        self.user = user

    async def update_select_menu(self, current: str = 'Menu', refresh: bool = True):
        if refresh:
            characters = await self.client.database.get_user_characters(self.user.id)

            self.select_menu.options.clear()
            menu_option = discord.SelectOption(label='Rizz Menu', value='Menu', description='Return to the Rizz Menu',
                                               emoji='📜')
            menu_option.default = current == 'Menu'
            self.select_menu.options.append(menu_option)

            for character in characters:
                profile = await self.client.database.rizz_profile.get(character.trait_oid)
                option = discord.SelectOption(label=profile.name, value=character.oid,
                                              description=f'{character.relationship}, {character.rizz} Rizz',
                                              emoji=CHARACTER_EMOJIS[character.relationship])
                option.default = current == character.oid
                self.select_menu.options.append(option)
        else:
            for option in self.select_menu.options:
                option.default = option.value == current

    @discord.ui.select()
    async def select_menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == 'Menu':
            await RizzMainMenu(client=self.client, user=self.user).send(interaction)
        else:
            await RizzProfileMenu(client=self.client, user=self.user, chr_oid=select.values[0]).send(interaction)


class RizzMainMenu(DynamicRizzMenu):
    async def send(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.update_select_menu()

        user_data = await self.client.database.users.get(self.user.id)
        characters = await self.client.database.get_user_characters(self.user.id)

        rizzing = next((x for x in characters if x.oid == user_data.rizzing), None)
        if rizzing is None:
            selected = 'No one lol. L.'
        else:
            rizzing_profile = await self.client.database.rizz_profile.get(rizzing.trait_oid)
            selected = f'{rizzing_profile.name} (`{rizzing.oid}`)'

        embed = utils.get_embed('rizzMenu', user=self.user, selected=selected)
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='Create new Character', style=discord.ButtonStyle.primary, emoji='🧬')
    async def create_new_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CharacterCreator(client=self.client, user=self.user))


class RizzProfileMenu(DynamicRizzMenu):
    def __init__(
            self,
            *,
            client: CuddlezBot,
            user: discord.User,
            chr_oid: str
    ):
        super().__init__(client=client, user=user)
        self.chr_oid = chr_oid

        self.profile = None
        self.character = None
        self.user_data = None

    async def send(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.update_select_menu(current=self.chr_oid)

        self.character = await self.client.database.rizz_characters.get(self.chr_oid)
        self.profile = await self.client.database.rizz_profile.get(self.character.trait_oid)
        self.user_data = await self.client.database.users.get(self.user.id)

        self.rizz_now.disabled = self.user_data.rizzing == self.chr_oid

        embed = utils.get_embed('rizzProfile', user=self.user, name=self.profile.name, biography=self.profile.biography,
                                job=self.profile.job, fav_song=self.profile.fav_song, fav_food=self.profile.fav_food,
                                interests=self.profile.interests, fun_fact=self.profile.fun_fact)
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='Rizz Now', style=discord.ButtonStyle.primary, emoji='😳')
    async def rizz_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_data.rizzing = self.chr_oid
        await interaction.response.send_message(f'Noted. Now rizzing {self.chr_oid}')

    @discord.ui.button(label='View Stats', style=discord.ButtonStyle.primary, emoji='📈')
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await RizzStatsMenu(client=self.client, user=self.user, chr_oid=self.chr_oid).send(interaction)

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger, emoji='🗑️')
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.client.database.rizz_characters.delete(self.chr_oid)
        if self.user_data.rizzing == self.chr_oid:
            self.user_data.rizzing = None
        await RizzMainMenu(client=self.client, user=self.user).send(interaction)
        await interaction.followup.send(f'Noted. Deleted {self.profile.name}.')


class RizzStatsMenu(DynamicRizzMenu):
    def __init__(
            self,
            *,
            client: CuddlezBot,
            user: discord.User,
            chr_oid: str
    ):
        super().__init__(client=client, user=user)
        self.chr_oid = chr_oid

        self.character = None
        self.profile = None
        self.user_data = None

    async def send(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.update_select_menu(current=self.chr_oid)

        self.character = await self.client.database.rizz_characters.get(self.chr_oid)
        self.profile = await self.client.database.rizz_profile.get(self.character.trait_oid)
        self.user_data = await self.client.database.users.get(self.user.id)

        embed = utils.get_embed('rizzStats', user=self.user, name=self.profile.name, rizz=self.character.rizz,
                                relationship=self.character.relationship, total_messages=self.character.total_messages)
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.danger, emoji='⬅️')
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await RizzProfileMenu(client=self.client, user=self.user, chr_oid=self.chr_oid).send(interaction)
