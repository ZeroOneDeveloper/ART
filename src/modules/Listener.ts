import { Extension, listener } from '@pikokr/command.ts'
import {
  ActivityType,
  CategoryChannel,
  ChannelType,
  Collection,
  TextChannel,
} from 'discord.js'

class Listener extends Extension {
  @listener({ event: 'ready' })
  async ready() {
    this.logger.info(`Logged in as ${this.client.user?.tag}`)
    await this.commandClient.fetchOwners()
    this.client.user?.setPresence({
      activities: [
        {
          name: '문의사항은 DM으로 해주세요!',
          type: ActivityType.Playing,
        },
      ],
    })
    const CHECK_CHANNELS = async () => {
      const GUILD = this.client.guilds.cache.get(process.env.GUILD!)
      if (!GUILD) return
      const CHANNELS = GUILD.channels.cache.filter(
        (x) =>
          x.type === ChannelType.GuildText &&
          x.parent?.name === '🎨【 작가채널 】' &&
          x.name.endsWith('작가')
      )
      CHANNELS.map((channel) => {
        const punishmentTime = new Date()
        ;(channel as TextChannel).messages
          .fetch({ limit: 1 })
          .then((messages) => {
            const LAST_MESSAGE = messages.last()
            if (!LAST_MESSAGE) {
              punishmentTime.setDate((channel.createdAt as Date).getDate() + 14)
            }
            if (LAST_MESSAGE!.author.id === this.client.user?.id) {
              punishmentTime.setDate(
                (LAST_MESSAGE!.createdAt as Date).getDate() + 1
              )
            } else {
              punishmentTime.setDate(
                (LAST_MESSAGE!.createdAt as Date).getDate() + 14
              )
            }
            if (new Date() > punishmentTime) {
              console.log(channel.name, punishmentTime)
            }
          })
      })
    }
    await CHECK_CHANNELS()
    // setInterval(CHECK_CHANNELS, 1000 * 60 * 10)
  }

  @listener({ event: 'applicationCommandInvokeError', emitter: 'cts' })
  async errorHandler(err: Error) {
    this.logger.error(err)
  }
}

export const setup = async () => {
  return new Listener()
}
