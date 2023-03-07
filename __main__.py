from discord import (
    ui,
    utils,
    Color,
    Embed,
    Client,
    Object,
    Intents,
    TextChannel,
    ButtonStyle,
    Interaction,
    app_commands,
    PermissionOverwrite,
)

import os
import asyncio
from pytz import timezone
from dotenv import load_dotenv
from typing import List, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(verbose=True)

database = AsyncIOMotorClient(os.getenv("MONGODB_URI")).get_database(
    os.getenv("MONGODB_NAME")
)


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
@app_commands.rename(channelName="작가채널_이름")
@app_commands.describe(channelName="자신의 채널의 이름을 정합니다.")
async def writerApply(interaction: Interaction, channelName: str) -> None:
    await interaction.response.defer()

    if await database["users"].find_one({"_id": str(interaction.user.id)}):
        await interaction.edit_original_response(
            embed=Embed(
                title="⚠️ Warning",
                description="이미 작가신청을 하셨습니다.",
                color=Color.red(),
            )
        )
        return

    class Confirm(ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None

        @ui.button(label="동의", style=ButtonStyle.green, emoji="✅")
        async def confirm(self, _interaction: Interaction, button: ui.Button):
            overwrites = {
                interaction.guild.default_role: PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    add_reactions=False,
                    view_channel=False,
                ),
                interaction.user: PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    add_reactions=True,
                    view_channel=True,
                ),
                utils.get(
                    interaction.guild.roles, id=int(os.getenv("VIEWER"))
                ): PermissionOverwrite(
                    read_messages=True,
                    send_messages=False,
                    add_reactions=True,
                    view_channel=True,
                ),
            }

            writerChannel: TextChannel = await interaction.guild.create_text_channel(
                name=f"{channelName}작가",
                category=utils.get(
                    interaction.guild.categories, id=int(os.getenv("WRITER_CATEGORY"))
                ),
                overwrites=overwrites,
            )

            await database["users"].insert_one(
                {
                    "_id": str(interaction.user.id),
                    "channel": str(writerChannel.id),
                    "joinedAt": datetime.now(tz=timezone("Asia/Seoul")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

            await _interaction.response.send_message(
                embed=Embed(
                    title="작가신청",
                    description=f"정상적으로 작가신청이 완료되었습니다.\n작가채널 : {writerChannel.mention}",
                    color=Color.green(),
                ),
                ephemeral=True,
            )
            self.value = True

        @ui.button(label="거부", style=ButtonStyle.red, emoji="⛔")
        async def cancel(self, _interaction: Interaction, button: ui.Button):
            await _interaction.response.send_message(
                embed=Embed(
                    title="작가신청",
                    description="작가신청이 취소되었습니다.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )
            self.value = False

    view = Confirm()

    await interaction.edit_original_response(
        embed=Embed(
            title="작가신청",
            description=f"작가 채널 이름 : `{channelName}작가`\n채널 생성 진행할까요?",
            color=Color.orange(),
        ),
        view=view,
    )

    while True:
        if view.timeout <= 0:
            await interaction.edit_original_response(
                embed=Embed(
                    title="작가신청",
                    description="시간이 초과되었습니다.",
                    color=Color.red(),
                )
            )
            return

        if view.value is not None:
            await interaction.delete_original_response()
            break

        await asyncio.sleep(1)
        view.timeout -= 1


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
