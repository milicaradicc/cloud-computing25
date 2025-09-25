import { Artist } from "../artists/artist.model";

export interface Song {
  Id:string,
  title: string;
  genres?: string[];
  coverImage?: string;
  artists: Artist[];
  description?: string;
  Album?: string;
  duration?:number,
  fileName:string,
  deleted:boolean,
}
