import { Artist } from "../artists/artist.model";
import { Album } from "./models/album.model";

export interface FilterResult{
  artists: Artist[];
  albums: Album[];
}