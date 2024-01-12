import { Schema, model } from "mongoose";

const ARTIST_SCHEMA = new Schema(
  {
    artistId: {
      type: String,
      required: true,
    },
    channelId: {
      type: String,
      required: true,
    },
    punished: {
      type: Array<string>,
      required: true,
    },
  },
  {
    versionKey: false,
  }
);

export const Artist = model("artist", ARTIST_SCHEMA);
