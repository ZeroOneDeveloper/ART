from discord.ext import commands, tasks

from main import ART


class Listener(commands.Cog):
    def __init__(self, bot: ART):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user} ({self.bot.user.id})")

    @tasks.loop(seconds=60)
    async def checkArtistChannel(self):
        pass


async def setup(bot: ART):
    await bot.add_cog(Listener(bot))
