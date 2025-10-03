import { Album } from "../content/models/album.model";

export interface Artist{
  Id: string;
  name: string;
  biography: string;
  genres: string[];
  Genre: string
}

export interface ArtistWithAlbums extends Artist {
  albums: Album[];
}
