import { Artist } from "../artists/artist.model";

export interface Song {
  id:string,
  title: string;
  genres?: string[];
  coverImage?: string;
  artists: Artist[];
  description?: string;
  album?: string;
  duration?:number,
  fileName:string,
}
