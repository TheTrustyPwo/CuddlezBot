import functools
from typing import Callable, Coroutine, Tuple, Any, Dict
import asyncio


def to_thread(func: Callable) -> Callable[[Any], Coroutine[Any, Any, Any]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
