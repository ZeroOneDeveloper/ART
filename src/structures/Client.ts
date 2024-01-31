import {
  CommandClient,
  Extension,
  applicationCommand,
  ownerOnly,
} from "@pikokr/command.ts";
import {
  ApplicationCommandType,
  ChatInputCommandInteraction,
} from "discord.js";

import path from "path";

class DevModule extends Extension {
  @ownerOnly
  @applicationCommand({
    type: ApplicationCommandType.ChatInput,
    name: "reload",
    description: "reload modules",
  })
  async reload(i: ChatInputCommandInteraction) {
    await i.deferReply();
    const result = await this.commandClient.registry.reloadModules();
    await i.editReply(
      `Succeed: ${result.filter((x) => x.result).length} Error: ${
        result.filter((x) => !x.result).length
      }`
    );
  }
}

export class ARTClient extends CommandClient {
  async setup() {
    await this.enableApplicationCommandsExtension({
      guilds: [process.env.GUILD!],
    });
    await this.registry.registerModule(new DevModule());

    await this.registry.loadAllModulesInDirectory(
      path.join(__dirname, "..", "modules")
    );
  }
}
