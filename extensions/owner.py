from discord.ext import commands

from main import ART


class Owner(commands.Cog):
    def __init__(self, bot: ART):
        self.bot = bot


async def setup(bot: ART):
    await bot.add_cog(Owner(bot))
