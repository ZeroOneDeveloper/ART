from discord import (
    ui,
    utils,
    Color,
    Embed,
    Client,
    Object,
    Member,
    Intents,
    Message,
    DMChannel,
    TextChannel,
    ButtonStyle,
    Interaction,
    app_commands,
    InteractionType,
    PermissionOverwrite,
    RawReactionActionEvent,
)

import os
import time
import asyncio
from pytz import timezone
from dotenv import load_dotenv
from typing import List, Tuple, Dict
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


@client.event
async def on_member_join(member: Member):
    await member.add_roles(
        utils.get(member.guild.roles, id=int(os.getenv("VIEWER"))),
    )


cache: Dict[str, float] = dict()


@client.event
async def on_message(message: Message):
    if message.author.bot:
        return
    if isinstance(message.channel, DMChannel):
        if cache.get(str(message.author.id)) is None:
            cache[str(message.author.id)] = time.time()
        else:
            if time.time() - cache[str(message.author.id)] < 300:
                await message.channel.send(
                    embed=Embed(
                        title="⚠️ Warning",
                        description="5분에 한번씩만 문의사항을 보낼 수 있습니다.",
                        color=Color.red(),
                    )
                )
                return
            cache[str(message.author.id)] = time.time()
        await message.channel.send(
            embed=Embed(
                title="✅ Success",
                description="정상적으로 문의사항이 전송 되었으며,\n해당 문의사항에 욕설 및 비속어 등이 포함될 경우,\n불이익이 적용될 수 있습니다.",
                color=Color.green(),
            )
        )
        await client.get_channel(int(os.getenv("CONTACT_CHANNEL"))).send(
            embed=Embed(
                title=f"📣 {str(message.author)} ({message.author.id})",
                description=f"**{message.content}**",
                color=Color.green(),
            ),
            files=[await attachment.to_file() for attachment in message.attachments],
        )


@client.event
async def on_member_join(member: Member):
    if member.guild.id == int(os.getenv("GUILD")):
        content = f"""
어서오세요 {member.mention}님, ART 서버에 오신 것을 환영합니다!
저희 서버는 __**그림러들을 위한 서버**__이며,  __**커미션 / 리퀘스트 / 그림**__등을 올리거나 구경할 수 있습니다!

<#{int(os.getenv("RULE_CHANNEL_ID"))}> 읽어주시고 메세지 밑 __**반응**__ 눌러주시면 곧바로 역할이 지급됩니다!
역할 지급에 문제가 있다면 __**@ PD**__ 나 __**@ VJ**__ 언급하면 도와드리겠습니다😊
그럼 많은 활동 부탁드려요!
        """
        await (client.get_channel(int(os.getenv("WELCOME_CHANNEL")))).send(
            content=content
        )
        await (client.get_channel(int(os.getenv("USER_COUNT_CHANNEL")))).edit(
            name=f"전체-멤버-{member.guild.member_count}"
        )


@client.event
async def on_member_remove(member: Member):
    if member.guild.id == int(os.getenv("GUILD")):
        await (client.get_channel(int(os.getenv("BYE_CHANNEL")))).send(
            content=f'{member.mention}\n{str(member)}'
        )
        await (client.get_channel(int(os.getenv("USER_COUNT_CHANNEL")))).edit(
            name=f"전체-멤버-{member.guild.member_count}"
        )


@client.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    if int(os.getenv("ROLES_MESSAGE_ID")) == int(payload.message_id):
        roles = {
            "🤝": int(os.getenv("CO_REQUEST_ID")),
            "🎨": int(os.getenv("REQUEST_ID")),
            "💸": int(os.getenv("COMMISSION_ID")),
            "🖼️": int(os.getenv("CO_WRITER_ID")),
        }
        await client.get_guild(payload.guild_id).get_member(payload.user_id).add_roles(
            utils.get(client.get_guild(payload.guild_id).roles, id=roles[payload.emoji.name])
        )


@client.event
async def on_interaction(interaction: Interaction):
    if interaction.type == InteractionType.component:
        if interaction.message.id == int(os.getenv("PUBLIC_MESSAGE_ID")):
            if (
                utils.get(interaction.guild.roles, id=int(os.getenv("VIEWER")))
                in interaction.user.roles
            ):
                await interaction.response.send_message(
                    embed=Embed(
                        title="⚠️ Warning",
                        description="이미 시청자 역할을 받으셨습니다.",
                        color=Color.red(),
                    ),
                    ephemeral=True,
                )
                return
            await interaction.user.add_roles(
                utils.get(interaction.guild.roles, id=int(os.getenv("VIEWER"))),
            )
            await interaction.response.send_message(
                embed=Embed(
                    title="✅ Success",
                    description="정상적으로 시청자 역할이 추가되었습니다.",
                    color=Color.green(),
                ),
                ephemeral=True,
            )


@client.tree.command(name="작가신청", description="자신의 작품을 올릴 수 있는 작가채널을 신청합니다.")
@app_commands.rename(channelName="작가채널_이름")
@app_commands.describe(channelName="자신의 채널의 이름을 정합니다.")
async def writerApply(interaction: Interaction, channelName: str):
    await interaction.response.defer()

    if await database["channel"].find_one(
        {"authors": {"$in": [str(interaction.user.id)]}}
    ):
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
            if self.value:
                return
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
                utils.get(
                    interaction.guild.roles, id=int(os.getenv("WRITER"))
                ): PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
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

            await database["channel"].insert_one(
                {
                    "_id": str(writerChannel.id),
                    "authors": [str(interaction.user.id)],
                    "joinedAt": datetime.now(tz=timezone("Asia/Seoul")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

            await interaction.user.add_roles(
                utils.get(interaction.guild.roles, id=int(os.getenv("WRITER"))),
            )
            await interaction.user.remove_roles(
                utils.get(interaction.guild.roles, id=int(os.getenv("VIEWER"))),
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


@client.tree.command(name="dm", description="( VJ ONLY ) 사용자에게 DM을 보냅니다.")
@app_commands.describe(user="DM을 보낼 사용자를 선택합니다.", content="전송할 내용을 입력합니다.")
@app_commands.rename(user="사용자", content="내용")
async def sendDm(interaction: Interaction, user: Member, *, content: str):
    if not utils.get(interaction.user.roles, id=int(os.getenv("VJ"))):
        await interaction.response.send_message(
            embed=Embed(
                title="⚠️ Warning",
                description="권한이 없습니다.",
                color=Color.red(),
            ),
            ephemeral=True,
        )
        return
    sendMessage = content.replace("  ", "\n")
    await user.send(
        embed=Embed(
            title="📨 DM",
            description=sendMessage,
            color=interaction.user.color,
        ).set_footer(text='DM으로 답장하시면 관리자에게 전달됩니다.'),
    )
    await interaction.response.send_message(
        embed=Embed(
            title="✅ Success",
            description="정상적으로 DM을 보냈습니다.",
            color=Color.green(),
        ),
    )


@client.tree.command(name="경고", description="( VJ ONLY ) 경고를 부여합니다.")
@app_commands.describe(channel="경고를 부여할 채널을 선택합니다.")
@app_commands.rename(channel="작가채널")
async def warn(interaction: Interaction, channel: TextChannel):
    if not utils.get(interaction.user.roles, id=int(os.getenv("VJ"))):
        await interaction.response.send_message(
            embed=Embed(
                title="⚠️ Warning",
                description="권한이 없습니다.",
                color=Color.red(),
            ),
            ephemeral=True,
        )
        return
    findData = await database["channel"].find_one({"_id": str(channel.id)})
    await channel.send(
        content=f"<@{findData['authors'][0]}>",
        embed=Embed(
            title="⚠️ 경고",
            description="장기간 미활동으로 24시간 후 채널 삭제합니다!\n그림 올리시면 보존되니 참고 바랍니다!\n"
            "`이 뒤로는 적어도 14일에 한번씩은 활동 부탁드려요!`",
            color=Color.red(),
        ),
    )
    await interaction.response.send_message(
        embed=Embed(
            title="경고",
            description=f"정상적으로 경고를 부여했습니다.",
            color=Color.green(),
        )
    )
    return


@client.tree.command(name="삭제", description="( VJ ONLY ) 작가채널을 삭제합니다.")
@app_commands.describe(channel="삭제할 채널을 선택합니다.")
@app_commands.rename(channel="작가채널")
async def deleteWriterChannel(interaction: Interaction, channel: TextChannel):
    if not utils.get(interaction.user.roles, id=int(os.getenv("VJ"))):
        await interaction.response.send_message(
            embed=Embed(
                title="⚠️ Warning",
                description="권한이 없습니다.",
                color=Color.red(),
            ),
            ephemeral=True,
        )
        return

    # confirm interaction
    class Confirm(ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.value = None

        @ui.button(label="확인", style=ButtonStyle.green, emoji="✅")
        async def confirm(self, _interaction: Interaction, button: ui.Button):
            self.value = True
            await _interaction.response.send_message(
                embed=Embed(
                    title="⚠️ Warning",
                    description="삭제중입니다...",
                    color=Color.orange(),
                ),
                ephemeral=True,
            )

        @ui.button(label="거부", style=ButtonStyle.red, emoji="⛔")
        async def cancel(self, _interaction: Interaction, button: ui.Button):
            self.value = False
            await _interaction.response.send_message(
                embed=Embed(
                    title="⚠️ Warning",
                    description="삭제를 취소했습니다.",
                    color=Color.red(),
                ),
                ephemeral=True,
            )

    view = Confirm()
    await interaction.response.send_message(
        embed=Embed(
            title="⚠️ Warning",
            description=f"정말로 다음 채널을 삭제할까요?\n채널 : {channel.mention}",
            color=Color.orange(),
        ),
        view=view,
    )
    while True:
        if view.timeout <= 0:
            await interaction.edit_original_response(
                embed=Embed(
                    title="⚠️ Warning",
                    description="시간이 초과되었습니다.",
                    color=Color.red(),
                )
            )
            return
        await asyncio.sleep(1)
        view.timeout -= 1
        if view.value is not None and view.value is True:
            await channel.delete()
            findData = await database["channel"].find_one({"_id": str(channel.id)})
            await database["channel"].delete_one({"_id": str(channel.id)})
            member = utils.get(
                interaction.guild.members, id=int(findData["authors"][0])
            )
            for role in [
                int(os.getenv("WRITER")),
                982907252103086191,
                982907265101201408,
                982907268389535745,
            ]:
                await member.remove_roles(
                    utils.get(interaction.guild.roles, id=int(role))
                )
            await member.add_roles(
                utils.get(interaction.guild.roles, id=int(os.getenv("VIEWER")))
            )
            await interaction.edit_original_response(
                embed=Embed(
                    title="✅ Success",
                    description=f"정상적으로 삭제했습니다.",
                    color=Color.green(),
                ),
                view=None,
            )
            return
        elif view.value is not None and view.value is False:
            await interaction.edit_original_response(
                embed=Embed(
                    title="⚠️ Warning",
                    description="삭제를 취소했습니다.",
                    color=Color.red(),
                ),
                view=None,
            )
            return


@client.tree.command(
    name="트래커", description="( VJ ONLY ) 작가채널의 마지막 메시지가 14일 이상 지났는지 확인합니다."
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
    trackedChannels: List[Tuple[TextChannel, datetime, int]] = []
    channelCount = 0
    for category in list(
        filter(lambda x: x.name == "🎨【 작가채널 】", interaction.guild.categories)
    ):
        for channel in category.channels:
            if not channel.name.endswith("작가"):
                continue
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
            if (lastSendTime + timedelta(days=14)) < datetime.now(
                tz=timezone("Asia/Seoul")
            ):
                try:
                    trackedChannels.append(
                        (channel, lastSendTime, messages[0].author.id)
                    )
                except IndexError:
                    trackedChannels.append(
                        (
                            channel,
                            lastSendTime,
                            (
                                await database["channel"].find_one(
                                    {"_id": str(channel.id)}
                                )
                            )["authors"][0],
                        )
                    )
    inNeedOfActionChannel = "\n".join(
        [
            f"{channel.mention} (<@{authorId}>) : {datetime.now(tz=timezone('Asia/Seoul')) - lastSendTime}"
            for channel, lastSendTime, authorId in trackedChannels
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


@client.tree.command(name="새로고침", description="( VJ ONLY ) 작가채널을 데이터베이스에 새로고침합니다.")
async def refresh(interaction: Interaction) -> None:
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
    abnormalChannels: List[TextChannel] = []
    for category in list(
        filter(lambda x: x.name == "🎨【 작가채널 】", interaction.guild.categories)
    ):
        for channel in category.channels:
            if str(channel.topic) == "":
                if (
                    await database["channel"].find_one({"channel": str(channel.id)})
                    is None
                ):
                    if channel.name.endswith("작가"):
                        abnormalChannels.append(channel)
                continue
            if await database["channel"].find_one({"_id": str(channel.id)}) is None:
                await database["channel"].insert_one(
                    {
                        "_id": str(channel.id),
                        "authors": [str(channel.topic)],
                        "joinedAt": channel.created_at.replace(
                            tzinfo=timezone("Asia/Seoul")
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                await channel.edit(topic="")
    if len(abnormalChannels) != 0:
        await interaction.edit_original_response(
            embed=Embed(
                title="작가채널 새로고침",
                description=f"정상적으로 작가채널을 새로고침 하였습니다.\n하지만, **{len(abnormalChannels)}** 개의 채널이\n"
                f"비정상적으로 작동하고 있습니다.\n\n{', '.join([channel.mention for channel in abnormalChannels])}",
                color=Color.red(),
            )
        )
        return
    await interaction.edit_original_response(
        embed=Embed(
            title="작가채널 새로고침",
            description="작가채널들을 데이터베이스에\n새로고침 하였습니다.",
            color=Color.green(),
        )
    )
    return


client.run(os.getenv("TOKEN"))
