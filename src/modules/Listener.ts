import { Extension, listener } from "@pikokr/command.ts";
import { ActivityType, ChannelType, TextChannel } from "discord.js";

class Listener extends Extension {
  @listener({ event: "ready" })
  async ready() {
    this.logger.info(`Logged in as ${this.client.user?.tag}`);
    await this.commandClient.fetchOwners();
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
      CHANNELS.map(async (channel) => {
        const punishmentTime = new Date();
        punishmentTime.setHours(punishmentTime.getHours() + 9);
        const lastMessage = (
          await (channel as TextChannel).messages.fetch({ limit: 1 })
        ).last();
        if (!lastMessage) {
          const channelCreatedAt = (channel as TextChannel).createdAt as Date;
          punishmentTime.setDate(channelCreatedAt.getDate() + 14);
          punishmentTime.setHours(channelCreatedAt.getHours());
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
          console.log(channel.name, punishmentTime);
        }
      });
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
