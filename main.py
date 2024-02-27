from discord import Intents, Object
from discord.ext.commands import AutoShardedBot

import os
from dotenv import load_dotenv

load_dotenv(verbose=True)


class ART(AutoShardedBot):
    def __init__(self):
        super().__init__(
            intents=Intents.all(),
            command_prefix='!',
            help_command=None,
        )

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(
            guild=Object(
                id=int(
                    os.getenv('GUILD')
                )
            )
        )
