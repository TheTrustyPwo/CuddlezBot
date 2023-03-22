import discord
import openai

from cuddlez.client import CuddlezBot
from cuddlez.commons.decorators import to_thread
from cuddlez.utils import utils


class MBTIGuesser:
    def __init__(
            self,
            *,
            client: CuddlezBot,
            user: discord.User,
    ):
        self.client = client
        self.user = user
        self.response = None
        self.messages = [
            {
                "role": "system",
                "content": "You have to try to guess the user's MBTI type. Ask exactly five personalized questions individually. After all questions have been answered, state and explain the most probable MBTI type."
            },
        ]

    async def start(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.respond('Start')
        embed = utils.get_embed('mbtiGuesser', user=self.user, content=self.response)
        await interaction.followup.send(embed=embed)

        for _ in range(5):
            answer = await self.client.wait_for('message', check=lambda
                msg: msg.author == self.user and msg.channel == interaction.channel, timeout=300.0)
            await answer.delete()
            await self.respond(answer.content)
            embed = utils.get_embed('mbtiGuesser', user=self.user, content=self.response)
            await interaction.edit_original_response(embed=embed)

    async def respond(self, prompt: str):
        self.messages.append({'role': 'user', 'content': prompt})
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        message = response.choices[0].message
        self.messages.append(message)
        self.response = message.content
