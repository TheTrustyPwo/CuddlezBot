import discord
from cuddlez.client import CuddlezBot
from cuddlez.cogs.rizz.profile import CharacterProfile
from cuddlez.cogs.rizz.character_data import CharacterData
from cuddlez.utils.utils import get_embed


class CharacterCreator(discord.ui.Modal, title='Character Creator'):
    def __init__(
            self,
            *,
            client: CuddlezBot,
            user: discord.User,
            timeout: float = 300.0
    ):
        super().__init__(timeout=timeout)
        self.client = client
        self.user = user

    description = discord.ui.TextInput(
        label='User description of the character',
        style=discord.TextStyle.long,
        placeholder='Personality, interests, job, background, etc.',
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=get_embed('creatingCharacter', content='Using magic to generate your new character...'))
        profile = await CharacterProfile.generate(self.description.value)
        await interaction.edit_original_response(embed=get_embed('creatingCharacter', content='Saving character profile...'))
        await self.client.database.rizz_profile.save(profile.oid, profile)
        await interaction.edit_original_response(embed=get_embed('creatingCharacter', content='Assigning you your new character...'))
        character = CharacterData(user_id=self.user.id, trait_oid=profile.oid)
        await self.client.database.rizz_characters.save(character.oid, character)
        await interaction.edit_original_response(embed=get_embed('creatingCharacter', content='Character creation successful! Head to `/rizz menu` to view your newly created character.'))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
