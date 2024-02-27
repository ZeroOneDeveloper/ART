from discord import CategoryChannel
from discord.ext import commands, tasks

from main import ART

import os
from typing import List
from pytz import timezone
from datetime import timedelta


class Listener(commands.Cog):
    def __init__(self, bot: ART):
        self.bot = bot
        self.database = bot.database
        self.checkArtistChannel.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user} ({self.bot.user.id})")

    @tasks.loop(seconds=10)
    async def checkArtistChannel(self):
        GUILD = self.bot.get_guild(int(os.getenv("GUILD")))
        if GUILD is None:
            return
        artistCategories: List[CategoryChannel] = list(
            filter(lambda x: x.name == "🎨【 작가채널 】", GUILD.channels)
        )
        if len(artistCategories) == 0:
            return
        punishedChannels = []
        for category in artistCategories:
            for channel in category.channels:
                if channel.name == "📢│중대발표":
                    continue
                messages = [message async for message in channel.history(limit=2)]
                print(
                    messages[0]
                    .created_at.replace(tzinfo=timezone("UTC"))
                    .astimezone(timezone("Asia/Seoul"))
                )
                if len(messages) == 0:
                    punishedTime = channel.created_at.replace(
                        tzinfo=timezone("UTC")
                    ).astimezone(timezone("Asia/Seoul"))
                else:
                    if messages[0].author.bot:
                        if len(messages) == 1:
                            punishedTime = channel.created_at.replace(
                                tzinfo=timezone("UTC")
                            ).astimezone(timezone("Asia/Seoul")) + timedelta(days=1)
                        else:
                            punishedTime = messages[1].created_at.replace(
                                tzinfo=timezone("UTC")
                            ).astimezone(timezone("Asia/Seoul")) + timedelta(days=1)
                    else:
                        punishedTime = messages[0].created_at.replace(
                            tzinfo=timezone("UTC")
                        ).astimezone(timezone("Asia/Seoul")) + timedelta(days=1)



async def setup(bot: ART):
    await bot.add_cog(Listener(bot))
