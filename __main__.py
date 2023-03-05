from discord import (
    utils,
    Color,
    Embed,
    Client,
    Object,
    Intents,
    TextChannel,
    Interaction,
    app_commands,
)

import os
from pytz import timezone
from dotenv import load_dotenv
from typing import List, Tuple
from datetime import datetime, timedelta


load_dotenv(verbose=True)


class MyClient(Client):
    def __init__(self):
        super().__init__(intents=Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        GUILD = Object(id=int(os.getenv("GUILD")))
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)


client = MyClient()


@client.event
async def on_ready():
    print(f"{str(client.user)} is ready.")


@client.tree.command(name="작가신청", description="자신의 작품을 올릴 수 있는 작가채널을 신청합니다.")
async def writerApply(interaction: Interaction):
    await interaction.response.defer()
    await interaction.edit_original_response(
        embed=Embed(
            title="작가신청",
            description="작가신청은 현재 준비중입니다.",
            color=Color.red(),
        )
    )


@client.tree.command(
    name="트래커", description="( VJ ONLY ) 작가채널의 마지막 메시지가 7일 이상 지났는지 확인합니다."
)
async def tracker(interaction: Interaction) -> None:
    if not (
        utils.get(interaction.guild.roles, id=int(os.getenv("VJ")))
        in interaction.user.roles
    ):
        await interaction.response.send_message(
            embed=Embed(
                title="⚠️ Warning",
                description=f'이 명령어는 <@&{os.getenv("VJ")}>만 사용할 수 있습니다.',
                color=Color.red(),
            ),
            ephemeral=True,
        )
        return
    await interaction.response.defer()
    trackedChannels: List[Tuple[TextChannel, datetime]] = []
    channelCount = 0
    for category in list(
        filter(lambda x: x.name == "🎨【 작가채널 】", interaction.guild.categories)
    ):
        for channel in category.channels:
            channelCount += 1
            messages = [message async for message in channel.history(limit=1)]
            if len(messages) == 0:
                lastSendTime: datetime = channel.created_at.replace(
                    tzinfo=timezone("Asia/Seoul")
                )
            else:
                lastSendTime: datetime = messages[0].created_at.replace(
                    tzinfo=timezone("Asia/Seoul")
                )
            if (lastSendTime + timedelta(days=7)) < datetime.now(
                tz=timezone("Asia/Seoul")
            ):
                trackedChannels.append((channel, lastSendTime))
    inNeedOfActionChannel = "\n".join(
        [
            f"{channel.mention} : {datetime.now(tz=timezone('Asia/Seoul')) - lastSendTime}"
            for channel, lastSendTime in trackedChannels
        ]
    )
    await interaction.edit_original_response(
        embed=Embed(
            title="작가채널 트래커",
            description=f"추적 채널 : {channelCount}개\n조치 필요 채널 : {len(trackedChannels)}개\n\n{inNeedOfActionChannel}",
            color=Color.red(),
        )
    )
    return


client.run(os.getenv("TOKEN"))
