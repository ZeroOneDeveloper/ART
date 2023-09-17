import {
  Interaction,
  ButtonStyle,
  ChannelType,
  ButtonBuilder,
  ActionRowBuilder,
  ApplicationCommandType,
  ChatInputCommandInteraction,
  ApplicationCommandOptionType,
  CategoryChannel,
} from "discord.js";
import { Extension, applicationCommand, option } from "@pikokr/command.ts";

import { Artist } from "../../Database/Schema";

class Commands extends Extension {
  @applicationCommand({
    type: ApplicationCommandType.ChatInput,
    name: "작가신청",
    description: "작가신청을 합니다.",
  })
  async apply(
    i: ChatInputCommandInteraction,
    @option({
      type: ApplicationCommandOptionType.String,
      required: true,
      name: "이름",
      description:
        "작가 신청할 이름을 입력해주세요. | ex) /작가신청 asdf -> asdf작가",
    })
    name: string
  ) {
    if (
      await Artist.findOne({
        artistIds: {
          $in: [i.user.id],
        },
      })
    ) {
      return i.reply({
        embeds: [
          {
            title: "작가신청 실패",
            description: "이미 작가신청을 하셨습니다.",
            color: 0xff0000,
          },
        ],
        ephemeral: true,
      });
    }
    const msg = await i.reply({
      embeds: [
        {
          title: "작가신청",
          description: `작가신청을 하시겠습니까?\n채널명 : \`${name}작가\`\n\n**비속어, 욕설 등이 포함된 채널명일 경우,\n경고 없이 삭제 조치될 수 있습니다.**`,
          color: 0xffa500,
        },
      ],
      components: [
        new ActionRowBuilder<ButtonBuilder>({
          components: [
            new ButtonBuilder()
              .setCustomId("confirm")
              .setLabel("동의")
              .setStyle(ButtonStyle.Success),
            new ButtonBuilder()
              .setCustomId("cancel")
              .setLabel("거부")
              .setStyle(ButtonStyle.Danger),
          ],
        }),
      ],
    });
    const filter = (interaction: Interaction) =>
      i.user.id === interaction.user.id;
    try {
      const confirmation = await msg.awaitMessageComponent({
        filter: filter,
        time: 60_000,
      });
      if (confirmation.customId === "confirm") {
        const ART_GUILD = this.client.guilds.cache.get(process.env.GUILD!)!;
        const ARTIST_CATEGORIES = ART_GUILD.channels.cache.filter(
          (c) => c.name === "🎨【 작가채널 】"
        );
        if (
          !ARTIST_CATEGORIES.size ||
          (ARTIST_CATEGORIES.size === 1 &&
            (ARTIST_CATEGORIES.first() as CategoryChannel).children.cache
              .size >= 50) ||
          (ARTIST_CATEGORIES.size > 1 &&
            (ARTIST_CATEGORIES.at(-2) as CategoryChannel).children.cache.size >=
              50 &&
            (ARTIST_CATEGORIES.at(-1) as CategoryChannel).children.cache.size >=
              50)
        ) {
          await ART_GUILD.channels.create({
            name: "🎨【 작가채널 】",
            type: ChannelType.GuildCategory,
          });
        }
        const createdChannel = await (
          ART_GUILD.channels.cache
            .filter((c) => c.name === "🎨【 작가채널 】")
            .last() as CategoryChannel
        ).children.create({
          name: `${name}작가`,
          type: ChannelType.GuildText,
          permissionOverwrites: [
            {
              id: ART_GUILD.roles.everyone.id,
              deny: [
                "ViewChannel",
                "ManageChannels",
                "ManageRoles",
                "ManageWebhooks",
                "CreateInstantInvite",
                "ReadMessageHistory",
                "SendMessages",
              ],
            },
            {
              id: ART_GUILD.roles.cache.find(
                (r) => r.id === process.env.VIEWER_ID!
              )!,
              allow: ["ViewChannel", "ReadMessageHistory"],
            },
            {
              id: ART_GUILD.roles.cache.find(
                (r) => r.id === process.env.ARTIST_ID!
              )!,
              allow: ["ViewChannel", "ReadMessageHistory"],
            },
            {
              id: ART_GUILD.members.cache.find((m) => m.id === i.user.id)!,
              allow: [
                "ViewChannel",
                "SendMessages",
                "ManageMessages",
                "ReadMessageHistory",
              ],
            },
          ],
        });
        const newArtist = new Artist({
          name: name,
          artistIds: [i.user.id],
          channelId: createdChannel.id,
        });
        await newArtist.save();
        await i.editReply({
          embeds: [
            {
              title: "작가신청 성공",
              description: "작가신청을 성공적으로 하셨습니다.",
              color: 0x00ff00,
            },
          ],
          components: [],
        });
      } else if (confirmation.customId === "cancel") {
        await i.editReply({
          embeds: [
            {
              title: "작가신청 실패",
              description: "작가신청을 취소하셨습니다.",
              color: 0xff0000,
            },
          ],
          components: [],
        });
      }
      return;
    } catch (e) {
      return await i.editReply({
        embeds: [
          {
            title: "작가신청 실패",
            description: "시간이 초과되었습니다.",
            color: 0xff0000,
          },
        ],
        components: [],
      });
    }
  }
}

export const setup = async () => {
  return new Commands();
};
