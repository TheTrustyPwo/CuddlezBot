import discord

from cuddlez.client import CuddlezBot
from cuddlez.utils import utils
from cuddlez.cogs.rizz.modals import CharacterCreator

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
            menu_option = discord.SelectOption(label='Rizz Menu', value='Menu', description='Return to the Rizz Menu', emoji='📜')
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
        raise NotImplementedError

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

    @discord.ui.select()
    async def select_menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == 'Menu':
            await self.send(interaction)
            return

        view = RizzProfileMenu(client=self.client, user=self.user, chr_oid=select.values[0])
        await view.send(interaction)

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

    async def send(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.update_select_menu(current=self.chr_oid)

        character = await self.client.database.rizz_characters.get(self.chr_oid)
        profile = await self.client.database.rizz_profile.get(character.trait_oid)
        rizzing = (await self.client.database.users.get(self.user.id)).rizzing

        self.rizz_now.disabled = rizzing == self.chr_oid

        embed = utils.get_embed('rizzProfile', user=self.user, name=profile.name, biography=profile.biography,
                                job=profile.job,
                                fav_song=profile.fav_song, fav_food=profile.fav_food, interests=profile.interests,
                                fun_fact=profile.fun_fact)
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.select()
    async def select_menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == 'Menu':
            view = RizzMainMenu(client=self.client, user=self.user)
            await view.send(interaction)
            return

        self.chr_oid = select.values[0]
        await self.send(interaction)

    @discord.ui.button(label='Rizz Now', style=discord.ButtonStyle.primary)
    async def rizz_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = await self.client.database.users.get(self.user.id)
        user_data.rizzing = self.chr_oid
        await interaction.response.send_message(f'Noted. Now rizzing {self.chr_oid}')

    @discord.ui.button(label='View Stats', style=discord.ButtonStyle.primary)
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('L. Not implemented yet.')

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('L. Not implemented yet.')
