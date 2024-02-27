from discord.ext import commands, tasks
from discord import Embed, Color, CategoryChannel

from main import ART

import os
from typing import List
from pytz import timezone
from datetime import datetime, timedelta


class Listener(commands.Cog):
    def __init__(self, bot: ART):
        self.bot = bot
        self.logger = bot.logger
        self.database = bot.database
        self.checkArtistChannel.start()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.bot.user} ({self.bot.user.id})")

    @tasks.loop(seconds=60)
    async def checkArtistChannel(self) -> None:
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
                if len(messages) == 0:
                    punishedTime = channel.created_at.replace(
                        tzinfo=timezone("UTC")
                    ).astimezone(timezone("Asia/Seoul")) + timedelta(days=14)
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
                        ).astimezone(timezone("Asia/Seoul")) + timedelta(days=14)
                if datetime.now().replace(tzinfo=timezone("Asia/Seoul")) > punishedTime:
                    punishedChannels.append(channel)
        noticedChannels = []
        for punishedChannel in punishedChannels:
            data = await self.database["artists"].find_one(
                {"channelId": str(punishedChannel.id)}
            )
            if len(data["punished"]) > 3:
                noticedChannels.append(punishedChannel)
            else:
                await self.database["artists"].update_one(
                    {"channelId": str(punishedChannel.id)},
                    {
                        "$push": {
                            "punished": datetime.now()
                            .replace(tzinfo=timezone("Asia/Seoul"))
                            .strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
                        }
                    },
                )
                await punishedChannel.send(
                    embed=Embed(
                        title='⚠️ 경고',
                        description='장기간 미활동으로 24시간 후 채널 삭제합니다!\n'
                                    '그림을 올리시면 보존되니 참고바랍니다!\n'
                                    '`이 뒤로는 적어도 14일에 한번씩은 활동 부탁드려요!`',
                        color=Color.red()
                    )
                )
        if len(noticedChannels) > 0:
            channels = "\n".join([channel.mention for channel in noticedChannels])
            await GUILD.get_channel(int(os.getenv("MANAGE_CHANNEL"))).send(
                embed=Embed(
                    title='⚠️ 채널 처리 요청',
                    description=f'🚨 미활동 채널 {len(noticedChannels)}개 발견됨\n'
                                f'📌\n{channels}',
                    color=Color.orange()
                )
            )


async def setup(bot: ART):
    await bot.add_cog(Listener(bot))
