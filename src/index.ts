import { ARTClient } from './structures'
import { Client } from 'discord.js'

require('dotenv').config()

const client = new Client({
  intents: ['Guilds', 'DirectMessages'],
})

const cts = new ARTClient(client)

const start = async () => {
  await cts.setup()

  await client.login(process.env.TOKEN)

  await cts.getApplicationCommandsExtension()?.sync()
}

start().then()
