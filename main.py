from discord import Intents, Object
from discord.ext.commands import AutoShardedBot, errors

import os
from dotenv import load_dotenv

from utilities import createLogger, getDatabase

load_dotenv(verbose=True)


class ART(AutoShardedBot):
    def __init__(self):
        super().__init__(
            intents=Intents.all(),
            command_prefix="!",
            help_command=None,
        )
        self.logger = createLogger("ART", 20)
        self.database = getDatabase(
            url=os.getenv("MONGO_DB_URL"),
            name=os.getenv("MONGO_DB_NAME"),
        )

    async def setup_hook(self):
        for path, dirs, files in os.walk("extensions"):
            for file in files:
                if file.endswith(".py"):
                    try:
                        await self.load_extension(
                            f'{path.replace("/", ".")}.{file[:-3]}'
                        )
                        self.logger.info(
                            f'Loaded extension: {path.replace("/", ".")}.{file[:-3]}'
                        )
                    except errors.NoEntryPointError:
                        self.logger.warning(
                            f'Failed to load extension: {path.replace("/", ".")}.{file[:-3]}'
                        )
        await self.tree.sync(guild=Object(id=os.getenv("GUILD")))


if __name__ == "__main__":
    ART().run(os.getenv("TOKEN"))
