import { Schema, model } from "mongoose";

const ARTIST_SCHEMA = new Schema(
  {
    name: {
      type: String,
      required: true,
    },
    artistIds: {
      type: Array<string>,
      required: true,
    },
    channelId: {
      type: String,
      required: true,
    },
  },
  {
    versionKey: false,
  }
);

export const Artist = model("Artist", ARTIST_SCHEMA);
