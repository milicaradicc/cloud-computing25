import { Artist } from "../../artists/artist.model";
import { Album } from "./album.model";


export interface FilterResult {
  albums: Album[];
  artists: Artist[];
}