import re
from typing import Any

import discord
import openai

from cuddlez.commons.decorators import to_thread
from cuddlez.utils import utils


class AdventureView(discord.ui.View):
    def __init__(
            self,
            *,
            user: discord.User,
            type: str = None,
            starting_prompt: str = None,
            timeout: float = 180.0,
    ):
        super().__init__(timeout=timeout)
        self.user = user
        self.type = type or 'Normal',
        self.starting_prompt = starting_prompt or 'Start the game with a unique story.'
        self.scenario = None
        self.image = None
        self.first = self.second = self.third = None
        self.messages = [
            {
                "role": "system",
                "content": f"Act as a {self.type} text adventure game. For each prompt, describe a scenario and give 3 possible actions to take.\n\nThis is return format:\n[scenario]\nPossible Actions:\n1) [Action 1]\n2) [Action 2]\n3) [Action 3]\n\nThe entire story should last about 15 prompts and be immersive and captivating."
            },
        ]

    async def start(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.generate(self.starting_prompt)
        embed = utils.get_embed('adventure', user=self.user, scenario=self.scenario, first=self.first,
                                second=self.second, third=self.third, image=self.image)
        await interaction.followup.send(embed=embed, view=self)

    async def update(self, interaction: discord.Interaction, prompt: str):
        if interaction.user != self.user:
            await interaction.response.send_message(embed=utils.get_embed('notYourMenu'), ephemeral=True)
            return

        await interaction.response.defer()
        await interaction.edit_original_response(embed=utils.get_embed('adventureLoading', user=self.user), view=self)
        await self.generate(prompt)

        embed = utils.get_embed('adventure', user=self.user, scenario=self.scenario, first=self.first,
                                second=self.second, third=self.third, image=self.image)
        await interaction.edit_original_response(embed=embed, view=self)

    @staticmethod
    def parse(response) -> tuple[str | Any, ...]:
        match = re.match('([\s\S]*)\n*Possible Actions:\n*1\) (.*)\n*2\).(.*)\n*3\) (.*)', response)
        return match.groups()

    async def generate(self, prompt: str):
        if len(self.messages) >= 11:
            self.messages.pop(1)
            self.messages.pop(1)

        self.messages.append({'role': 'user', 'content': prompt})
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        message = response.choices[0].message
        self.messages.append(message)

        print(message.content)
        self.scenario, self.first, self.second, self.third = self.parse(message.content.strip())
        try:
            response = await openai.Image.acreate(
                prompt=self.scenario,
                n=1,
                size='1024x1024'
            )
            self.image = response.data[0].url
        except openai.error.InvalidRequestError:
            self.image = 'https://www.slntechnologies.com/wp-content/uploads/2017/08/ef3-placeholder-image.jpg'

    @discord.ui.button(emoji='1️⃣', style=discord.ButtonStyle.primary)
    async def action_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, self.first)

    @discord.ui.button(emoji='2️⃣', style=discord.ButtonStyle.primary)
    async def action_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, self.second)

    @discord.ui.button(emoji='3️⃣', style=discord.ButtonStyle.primary)
    async def action_three(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update(interaction, self.third)
