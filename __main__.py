from discord import Client, Intents, app_commands, Object

import json

from utilities import getLogger

with open(file='./config.json', mode='r', encoding='utf-8') as f:
    config = json.load(f)


class ART(Client):
    def __init__(self, intents: Intents):
        super().__init__(
            intents=intents
        )
        self.tree = app_commands.CommandTree(self)
        self.logger = getLogger(name='ART', level=config['LOG_LEVEL'])

    async def on_ready(self):
        self.logger.info(f'{self.user} is ready!')

    async def setup_hook(self):
        GUILD = Object(id=int(config['GUILD']))
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)


client = ART(intents=Intents.all())

if __name__ == '__main__':
    client.run(config['TOKEN'])
