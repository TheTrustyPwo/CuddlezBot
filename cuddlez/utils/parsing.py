import re
from typing import Union

suffixes = {
    'k': 1000,
    'm': 1000000,
    'b': 1000000000,
    't': 1000000000000
}

pb_emojis = {
    'start': {
        'filled': '<:PBSF:1085902078641188884>',
        'empty': '<:PBSE:1085902833259384995>'
    },
    'center': {
        'filled': '<:PBCF:1085902073192783882>',
        'empty': '<:PBCE:1085902828092014602>'
    },
    'end': {
        'filled': '<:PBEF:1085902076611145748>',
        'empty': '<:PFEE:1085902831338401843>'
    }
}


def parse_number(number_str: str, relative: int = None) -> Union[int, None]:
    if number_str in ('all', 'max'):
        return relative
    try:
        return int(number_str)
    except ValueError:
        match = re.search('^(\d+\.?\d+?)([a-zA-Z%])$', number_str)
        if match is None:
            return None
        number, suffix = match.group(1), match.group(2).lower()
        if suffix in suffixes:
            return int(float(number) * suffixes[suffix])
        if suffix == '%' and relative is not None:
            return int(float(number) / 100 * relative)
        return None

def progress_bar(progress: float, units: int = 10) -> str:
    filled = [pb_emojis['start']['filled']] + [pb_emojis['center']['filled'] for _ in range(2, units)] + [pb_emojis['end']['filled']]
    empty = [pb_emojis['start']['empty']] + [pb_emojis['center']['empty'] for _ in range(2, units)] + [pb_emojis['end']['empty']]
    units_filled = int(progress * units)
    bar = filled[:units_filled] + empty[units_filled:]
    return ''.join(bar)
