import { Artist } from "../artists/artist.model";
import { Song } from "./song.model";

export interface Album {
  title: string;
  coverImage: File;
  releaseDate: Date;
  songs: Song[];
  artists: Artist[];
  genres?: string[];
}