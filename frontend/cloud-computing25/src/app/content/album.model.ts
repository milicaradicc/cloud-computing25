import { Artist } from "../artists/artist.model";
import { Song } from "./song.model";

export interface Album {
  title: string;
  description?: string;
  coverImage: string;
  releaseDate: Date;
  songs: Song[];
  artists: Artist[];
  genres?: string[];
  id:string
}