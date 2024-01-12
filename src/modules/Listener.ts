import { TextChannel } from "discord.js";
import { Extension, listener } from "@pikokr/command.ts";

import mongoose from "mongoose";

let data: string[] = [];

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
      const punishedChannels: string[] = [];
      const GUILD = this.client.guilds.cache.get(process.env.GUILD!);
      if (!GUILD) return;
      const CHANNELS = GUILD.channels.cache.filter(
        (x) =>
          x.type === 0 &&
          x.parent?.name === "🎨【 작가채널 】" &&
          x.name.endsWith("작가")
      );
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
          if (lastMessage.author.id === this.client.user?.id) {
            punishmentTime.setDate(lastMessageCreatedAt.getDate() + 1);
          } else {
            punishmentTime.setDate(lastMessageCreatedAt.getDate() + 14);
          }
        }
        if (new Date() > punishmentTime) {
          if (!punishedChannels.includes(channel.id.toString())) {
            punishedChannels.push(channel.id.toString());
          }
        }
      });
      if (punishedChannels.sort() !== punishedChannels.sort()) {
        await (
          this.client.channels.cache.get("996824873009680425") as TextChannel
        ).send({
          embeds: [
            {
              title: "⚠️ 경고 조치 요망",
              description: punishedChannels.map((x) => `<#${x}>`).join("\n"),
              color: 0xff9900,
            },
          ],
        });
        data = punishedChannels;
      }
    };
    await CHECK_CHANNELS();
    setInterval(CHECK_CHANNELS, 1000 * 60);
  }

  @listener({ event: "applicationCommandInvokeError", emitter: "cts" })
  async errorHandler(err: Error) {
    this.logger.error(err);
  }
}

export const setup = async () => {
  return new Listener();
};

export default data;
