import {
  GuildMember,
  GuildMemberRoleManager,
  Interaction,
  TextChannel,
} from "discord.js";
import { Extension, listener } from "@pikokr/command.ts";

import mongoose from "mongoose";

import { Artist } from "../../database/Schema";

class Listener extends Extension {
  @listener({ event: "ready" })
  async ready() {
    await this.commandClient.fetchOwners();
    await mongoose.connect(process.env.MONGODB_URI!);
    this.logger.info(`Logged in as ${this.client.user?.tag}`);
    this.client.user?.setPresence({
      activities: [
        {
          name: "문의사항은 DM으로 해주세요!",
          type: 0,
        },
      ],
    });
    const CHECK_CHANNELS = async () => {
      const GUILD = this.client.guilds.cache.get(process.env.GUILD!);
      if (!GUILD) return;
      const CHANNELS = GUILD.channels.cache.filter(
        (x) =>
          x.type === 0 &&
          x.parent?.name === "🎨【 작가채널 】" &&
          x.name.endsWith("작가")
      );
      const punishedChannels = await Promise.all(
        CHANNELS.map(async (channel) => {
          const punishmentTime = new Date();
          punishmentTime.setHours(punishmentTime.getHours() + 9);
          const lastMessage = (
            await (channel as TextChannel).messages.fetch({ limit: 1 })
          ).last();
          if (!lastMessage) {
            const channelCreatedAt = (channel as TextChannel).createdAt as Date;
            punishmentTime.setDate(channelCreatedAt.getDate() + 14);
            punishmentTime.setHours(channelCreatedAt.getHours() + 9);
            punishmentTime.setMinutes(channelCreatedAt.getMinutes());
            punishmentTime.setSeconds(channelCreatedAt.getSeconds());
          } else {
            const lastMessageCreatedAt = lastMessage.createdAt as Date;
            lastMessageCreatedAt.setHours(lastMessageCreatedAt.getHours() + 9);
            punishmentTime.setHours(lastMessageCreatedAt.getHours());
            punishmentTime.setMinutes(lastMessageCreatedAt.getMinutes());
            punishmentTime.setSeconds(lastMessageCreatedAt.getSeconds());
            if (lastMessage.author.id !== this.client.user?.id) {
              punishmentTime.setDate(lastMessageCreatedAt.getDate() + 1);
              if (new Date() > punishmentTime) {
                return channel.id;
              }
            } else {
              punishmentTime.setDate(lastMessageCreatedAt.getDate() + 14);
            }
          }
          if (new Date() > punishmentTime) {
            const channelData = await Artist.findOne({
              channelId: channel.id,
            });
            if (!channelData) return undefined;
            if (channelData.get("punished").length >= 3) {
              return channel.id;
            }
            await (channel as TextChannel).send({
              content: `<@${channelData.get("artistId")}>`,
              embeds: [
                {
                  title: "⚠️ 경고",
                  description:
                    "장기간 미활동으로 24시간 후 채널 삭제합니다!\n그림을 올리시면 보존되니 참고바랍니다!\n`이 뒤로는 적어도 14일에 한번씩은 활동 부탁드려요!`",
                  color: 0xff0000,
                },
              ],
            });
          }
        })
      );
      if (
        punishedChannels.filter((x) => {
          return x !== undefined;
        }) !== []
      ) {
        await (
          GUILD.channels.cache.get("996824873009680425") as TextChannel
        ).send({
          embeds: [
            {
              title: "⚠️ 채널 처리 요청",
              description: punishedChannels
                .filter((x) => {
                  return x !== undefined;
                })
                .map((x) => `<#${x}>`)
                .join("\n"),
              color: 0xffa500,
            },
          ],
        });
      }
    };
    await CHECK_CHANNELS();
    setInterval(CHECK_CHANNELS, 1000 * 60 * 60 * 12);
  }

  @listener({ event: "applicationCommandInvokeError", emitter: "cts" })
  async errorHandler(err: Error) {
    this.logger.error(err);
  }

  @listener({ event: "guildMemberAdd" })
  async guildMemberAdd(member: GuildMember) {
    const WELCOME_CHANNEL =
      this.client.channels.cache.get("979041309610377246");
    if (!WELCOME_CHANNEL) return;
    await (WELCOME_CHANNEL as TextChannel).send({
      content: `어서오세요 <@${member.id}>님, ART 서버에 오신 것을 환영합니다!\n저희 서버는 **__그림러들을 위한 서버__**이며,  **__커미션 / 리퀘스트 / 그림__**등을 올리거나 구경할 수 있습니다!\n\n<#704031848170520668> 읽어주시고 메세지 밑 반응 눌러주시면 곧바로 역할이 지급됩니다!\n역할 지급에 문제가 있다면 **__@ PD__** 나 **__@ VJ__** 언급하면 도와드리겠습니다😊\n그럼 많은 활동 부탁드려요!`,
    });
  }

  @listener({ event: "guildMemberRemove" })
  async guildMemberRemove(member: GuildMember) {
    const BYE_CHANNEL = this.client.channels.cache.get("979041857109647401");
    if (!BYE_CHANNEL) return;
    await (BYE_CHANNEL as TextChannel).send({
      content: `<@${member.id}>\n${member.user.username}`,
    });
  }

  @listener({ event: "interactionCreate" })
  async interactionCreate(interaction: Interaction) {
    if (
      interaction.type === 3 &&
      interaction.channelId === "704031848170520668"
    ) {
      if (
        (interaction.member?.roles as GuildMemberRoleManager).cache.has(
          process.env.VIEWER_ID!
        )
      )
        await interaction.reply({
          content: "이미 역할이 지급되었습니다!",
          ephemeral: true,
        });
      await (interaction.member?.roles as GuildMemberRoleManager).add(
        process.env.VIEWER_ID!
      );
      await interaction.reply({
        content: "역할이 지급되었습니다!",
        ephemeral: true,
      });
    }
  }
}

export const setup = async () => {
  return new Listener();
};
