import { Album } from "../content/models/album.model";
import { Artist } from "./artist.model";

export interface ArtistWithAlbums {
  artist: Artist;
  albums: Album[];
}