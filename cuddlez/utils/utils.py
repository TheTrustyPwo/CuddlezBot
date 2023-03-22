import discord
import json
import datetime
import copy

from cuddlez.commons.config import Config


def get_embed(identifier: str, **kwargs) -> discord.Embed:
    embed_data = copy.deepcopy(Config().get('embeds', identifier))

    def set_placeholders(data: dict) -> None:
        """Recursive method to set template variables"""
        for template, actual in kwargs.copy().items():
            if isinstance(actual, int):
                kwargs[template] = '{:,}'.format(actual)
            elif isinstance(actual, float):
                kwargs[template] = '{:,.2f}'.format(actual)
            elif isinstance(actual, discord.Member):
                kwargs.update({
                    template: actual.name,
                    'user_id': str(actual.id),
                    'user_discriminator': str(actual.discriminator),
                    'user_mention': actual.mention,
                    'user_pfp': actual.avatar.url,
                })

        for key, value in data.items():
            if key == 'color':
                data['color'] = {"DEFAULT": 0xFFA500, "ERROR": 0xFF5555, "SUCCESS": 0x25DE1F}["DEFAULT"]
            elif key == 'timestamp' and value:
                data['timestamp'] = datetime.datetime.utcnow().isoformat()

            elif isinstance(value, str):
                for template, actual in kwargs.items():
                    value = value.replace('{' + template + '}', actual)
                data[key] = value

            elif isinstance(value, dict):
                set_placeholders(value)
                data[key] = value
            elif isinstance(value, list):
                for item in value:
                    set_placeholders(item)
                data[key] = value

    set_placeholders(embed_data)
    return discord.Embed.from_dict(embed_data)
