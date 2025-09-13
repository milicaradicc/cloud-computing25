import { Artist } from "../artists/artist.model";

export interface Song {
  title: string;
  genres?: string[];
  coverImage?: File;
  artists: Artist[];
  description?: string;
  album?: string;
}
