from typing import Union

import discord
from akinator import AsyncAkinator, Language, Theme, Answer, CantGoBackAnyFurther

from cuddlez.utils import utils, parsing


class AkinatorView(discord.ui.View):
    def __init__(
            self,
            *,
            user: discord.User,
            theme: Union[str, None] = None,
            language: Union[str, None] = None,
            timeout: float = 30.0
    ):
        super().__init__(timeout=timeout)
        self.user = user
        theme = theme or 'Characters'
        language = language or 'English'
        self.akinator = AsyncAkinator(language=Language.from_str(language), theme=Theme.from_str(theme))

    async def send(self, interaction: discord.Interaction):
        first_question = await self.akinator.start_game()
        embed = utils.get_embed('akinator', user=interaction.user, question=first_question,
                                progress=parsing.progress_bar(self.akinator.progression / 80, 15),
                                step=self.akinator.step + 1)
        await interaction.followup.send(embed=embed, view=self)

    async def update(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message(embed=utils.get_embed('notYourMenu'), ephemeral=True)
            return

        if self.akinator.progression > 80:
            self.stop()
            for button in self.children:
                button.disabled = True

            guess = await self.akinator.win()
            embed = utils.get_embed('akinatorFinish', user=interaction.user,
                                    name=guess.name, description=guess.description, image=guess.absolute_picture_path)
            await interaction.response.edit_message(embed=embed, view=self)
            return
        embed = utils.get_embed('akinator', user=interaction.user, question=self.akinator.question,
                                progress=parsing.progress_bar(self.akinator.progression / 80, 15),
                                step=self.akinator.step + 1)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Yes", emoji="👍", style=discord.ButtonStyle.primary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.akinator.answer(Answer.from_str('Yes'))
        await self.update(interaction)

    @discord.ui.button(label="No", emoji="👎", style=discord.ButtonStyle.primary)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.akinator.answer(Answer.from_str('No'))
        await self.update(interaction)

    @discord.ui.button(label="Idk", emoji="❔", style=discord.ButtonStyle.primary)
    async def idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.akinator.answer(Answer.from_str('Idk'))
        await self.update(interaction)

    @discord.ui.button(label="Probably", emoji="🤔", style=discord.ButtonStyle.primary)
    async def probably(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.akinator.answer(Answer.from_str('Probably'))
        await self.update(interaction)

    @discord.ui.button(label="Probably Not", emoji="🙄", style=discord.ButtonStyle.primary)
    async def probably_not(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.akinator.answer(Answer.from_str('Probably Not'))
        await self.update(interaction)

    @discord.ui.button(label="Back", emoji='⬅️', style=discord.ButtonStyle.danger, row=1)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.akinator.back()
            await self.update(interaction)
        except CantGoBackAnyFurther:
            await interaction.response.send_message('Cannot go back any further!', ephemeral=True)

    @discord.ui.button(label="Quit", emoji='🛑', style=discord.ButtonStyle.danger, row=1)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(view=self)
