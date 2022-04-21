import json
import anyio
import asyncio

from os import path, curdir, mkdir
from typing import Union
from discord.ext.i18n.language import Language


class Cache:
    def __init__(self, dir="__lang_cache__", filename="cache.json") -> None:
        self.cache_dir = path.join(curdir, dir)
        self.cache_fn = filename
        self.cache_pth = path.join(self.cache_dir, self.cache_fn)
        if not path.isdir(self.cache_dir):
            if mkdir(dir) == 1:
                raise ValueError(f"Could not make a cache folder at {self.cache_dir}")
        with open(self.cache_pth, mode="r", encoding="utf-8") as f:
            self.internal_cache = json.load(f)

    async def load_cache(self):
        if not path.isfile(self.cache_pth):
            await self.empty()
        else:
            f = await anyio.open_file(self.cache_pth, mode="r", encoding="utf-8")
            self.internal_cache = json.loads(await f.read())
            await f.aclose()

    async def save_cache(self):
        f = await anyio.open_file(self.cache_pth, mode="w", encoding="utf-8")
        await f.write(json.dumps(self.internal_cache))
        await f.aclose()

    async def empty(self):
        """
        Empty the internal and external cache.
        """
        f = await anyio.open_file(self.cache_pth, mode="w", encoding="utf-8")
        await f.write("{}")
        await f.aclose()
        self.internal_cache = {}

    def set_cache(
        self, src: Union[str, bytes], lang: Language, translated: Union[str, bytes]
    ):
        if src in self.internal_cache:
            self.internal_cache[src][lang.code] = translated
        else:
            self.internal_cache[src] = {lang.code: translated}
        asyncio.create_task(self.save_cache())

    def get_cache(self, src: Union[str, bytes], lang: Language):
        if src in self.internal_cache and lang.code in self.internal_cache[src]:
            return self.internal_cache[src][lang.code]
